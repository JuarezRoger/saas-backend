from django.shortcuts import render
from rest_framework import viewsets
from .models import Cliente, Servicio, Cotizacion
from .serializers import ClienteSerializer, ServicioSerializer, CotizacionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Compania

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