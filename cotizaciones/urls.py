# cotizaciones/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Importa CotizacionViewSet
from .views import ClienteViewSet, ServicioViewSet, CotizacionViewSet
from .views import cambiar_password

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'servicios', ServicioViewSet, basename='servicio')
router.register(r'cotizaciones', CotizacionViewSet, basename='cotizacion')

urlpatterns = [
    path('', include(router.urls)),
    path('cambiar-password/', cambiar_password, name='cambiar_password'),
]