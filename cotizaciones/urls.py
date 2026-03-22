# cotizaciones/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Importa CotizacionViewSet
from .views import ClienteViewSet, ServicioViewSet, CotizacionViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'servicios', ServicioViewSet, basename='servicio')
# NUEVO: Registramos las cotizaciones
router.register(r'cotizaciones', CotizacionViewSet, basename='cotizacion')

urlpatterns = [
    path('', include(router.urls)),
]