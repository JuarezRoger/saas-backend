from django.shortcuts import render

# Create your views here.

# cotizaciones/views.py
from rest_framework import viewsets
# Asegúrate de importar Cotizacion y CotizacionSerializer:
from .models import Cliente, Servicio, Cotizacion
from .serializers import ClienteSerializer, ServicioSerializer, CotizacionSerializer

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