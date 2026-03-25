"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# Modifica tu importación actual para que incluya CotizacionDetalleView
from cotizaciones.views import RegistroSaaSView, EnviarCotizacionView, CotizacionDetalleView, ClienteDetalleView, ServicioDetalleView

# Importamos la nueva vista que acabamos de crear
from cotizaciones.views import RegistroSaaSView 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 🌟 PASE VIP: Ponemos las rutas específicas ARRIBA para que Django las lea primero
    path('api/cotizaciones/<int:pk>/enviar/', EnviarCotizacionView.as_view(), name='enviar_cotizacion'),
    path('api/cotizaciones/<int:pk>/', CotizacionDetalleView.as_view(), name='cotizacion_detalle'),
    path('api/clientes/<int:pk>/', ClienteDetalleView.as_view(), name='cliente_detalle'),
    path('api/servicios/<int:pk>/', ServicioDetalleView.as_view(), name='servicio_detalle'),

    # Ahora sí, el resto de las rutas generales
    path('api/', include('cotizaciones.urls')),
    
    # Rutas de Tokens (Login)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registro
    path('api/registro/', RegistroSaaSView.as_view(), name='registro_saas'),


]