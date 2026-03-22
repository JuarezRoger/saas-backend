from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# 1. La tabla principal del SaaS
class Compania(models.Model):
    nombre = models.CharField(max_length=100)
    # Conectamos la compañía con el usuario que se registra
    usuario_dueno = models.OneToOneField(User, on_delete=models.CASCADE)
    plan_actual = models.CharField(max_length=20, default='Gratis')

    def __str__(self):
        return self.nombre

# 2. Los clientes de esa compañía
class Cliente(models.Model):
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE) # Seguridad Multi-tenant
    nombre_empresa = models.CharField(max_length=150)
    email = models.EmailField()

    def __str__(self):
        return self.nombre_empresa

# 3. Los servicios que vende la compañía
class Servicio(models.Model):
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2) # Hasta 99 millones, con 2 decimales

    def __str__(self):
        return self.nombre

# 4. La Cotización en sí
class Cotizacion(models.Model):
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True) # Se llena sola con la fecha actual
    estado = models.CharField(max_length=20, default='Borrador')

    def __str__(self):
        return f"{self.codigo} - {self.cliente.nombre_empresa}"

class DetalleCotizacion(models.Model):
    # Conectamos el detalle con la Cotización padre
    cotizacion = models.ForeignKey(Cotizacion, related_name='detalles', on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad}x {self.servicio.nombre}"