from django.shortcuts import render
from rest_framework import viewsets
from .models import Cliente, Servicio, Cotizacion
from .serializers import ClienteSerializer, ServicioSerializer, CotizacionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Compania
from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework import generics

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    
    # NUEVO: Reemplazamos queryset = Cliente.objects.all() por esto:
    def get_queryset(self):
        # self.request.user contiene al usuario dueño del Token JWT actual
        usuario_actual = self.request.user
        
        # Filtramos: Solo clientes cuya compañía tenga como dueño al usuario actual
        return Cliente.objects.filter(compania__usuario_dueno=usuario_actual)
    
        # NUEVO: Interceptamos la creación del cliente
    def perform_create(self, serializer):
        # Buscamos la compañía del usuario actual
        compania_del_usuario = self.request.user.compania
        # Guardamos el cliente forzando que se asigne a esa compañía
        serializer.save(compania=compania_del_usuario)

class ServicioViewSet(viewsets.ModelViewSet):
    serializer_class = ServicioSerializer
    
    def get_queryset(self):
        usuario_actual = self.request.user
        return Servicio.objects.filter(compania__usuario_dueno=usuario_actual)
    
        # NUEVO: Interceptamos la creación del cliente
    def perform_create(self, serializer):
        # Buscamos la compañía del usuario actual
        compania_del_usuario = self.request.user.compania
        # Guardamos el cliente forzando que se asigne a esa compañía
        serializer.save(compania=compania_del_usuario)

class CotizacionViewSet(viewsets.ModelViewSet):
    serializer_class = CotizacionSerializer

    def get_queryset(self):
        usuario_actual = self.request.user
        return Cotizacion.objects.filter(compania__usuario_dueno=usuario_actual)

    def perform_create(self, serializer):
        # Le inyectamos la compañía automáticamente por seguridad
        serializer.save(compania=self.request.user.compania)

class RegistroSaaSView(APIView):
    # Esto es vital: le decimos a Django que NO pida token para esta ruta
    # (¡Porque el usuario apenas se está registrando y no tiene token aún!)
    permission_classes = [] 

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        nombre_compania = request.data.get('nombre_compania')

        # Validar que vengan todos los datos
        if not all([username, password, email, nombre_compania]):
            return Response({'error': 'Faltan datos. Llena todos los campos.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar que el usuario no exista ya
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Ese nombre de usuario ya está en uso.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Creamos al usuario con su contraseña encriptada automáticamente
            nuevo_usuario = User.objects.create_user(username=username, email=email, password=password)
            
            # 2. Creamos la compañía y la vinculamos al usuario recién nacido
            Compania.objects.create(nombre=nombre_compania, usuario_dueno=nuevo_usuario)
            
            return Response({'mensaje': '¡Bienvenido a AtomSaaS! Cuenta creada.'}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EnviarCotizacionView(APIView):
    def post(self, request, pk):
        try:
            # Buscamos la cotización y aseguramos que pertenezca a la empresa del usuario
            # (¡Aquí cambiamos "empresa=" por "compania="!)
            cotizacion = Cotizacion.objects.get(pk=pk, compania=request.user.compania)
            cliente = cotizacion.cliente
            
            # Recibimos el PDF que nos manda React (en formato Base64)
            pdf_base64 = request.data.get('pdf')
            if not pdf_base64:
                return Response({'error': 'No se recibió el archivo PDF.'}, status=status.HTTP_400_BAD_REQUEST)

            # Limpiamos el texto base64 para que el correo lo entienda
            import base64
            formato, imgstr = pdf_base64.split(';base64,') 
            pdf_data = base64.b64decode(imgstr)

            # Preparamos el correo
            asunto = f'Cotización de Servicios - {request.user.compania.nombre}'
            mensaje = f'Hola {cliente.nombre_empresa},\n\nAdjunto encontrarás la cotización solicitada de parte de {request.user.compania.nombre}.\n\nSaludos cordiales.'
            remitente = settings.EMAIL_HOST_USER
            destinatario = [cliente.email]

            # Creamos el paquete del correo
            email = EmailMessage(asunto, mensaje, remitente, destinatario)
            # Adjuntamos el PDF decodificado
            email.attach(f'Cotizacion_{cotizacion.codigo}.pdf', pdf_data, 'application/pdf')
            # ¡Y lo enviamos!
            email.send()

            return Response({'mensaje': 'Correo enviado exitosamente a ' + cliente.email}, status=status.HTTP_200_OK)

        except Cotizacion.DoesNotExist:
            return Response({'error': 'Cotización no encontrada o no tienes permiso.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


# ==========================================
# NUEVA VISTA: Para Editar/Borrar una cotización específica
# ==========================================
class CotizacionDetalleView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CotizacionSerializer
    
    def get_queryset(self):
        # Medida de seguridad: que la agencia solo pueda editar sus propias cotizaciones
        return Cotizacion.objects.filter(compania=self.request.user.compania)