from django.contrib import admin

# Register your models here.

from django.contrib import admin
# 1. Importamos los modelos que creamos en el paso anterior
from .models import Compania, Cliente, Servicio, Cotizacion

# 2. Le decimos a Django que los registre en el panel visual
admin.site.register(Compania)
admin.site.register(Cliente)
admin.site.register(Servicio)
admin.site.register(Cotizacion)