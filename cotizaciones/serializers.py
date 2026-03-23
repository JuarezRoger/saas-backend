# cotizaciones/serializers.py
from rest_framework import serializers
from .models import Cliente, Servicio, Cotizacion, DetalleCotizacion

# --- SERIALIZADORES ANTIGUOS (No los borramos) ---

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ['compania'] 

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'
        read_only_fields = ['compania']


# --- NUEVOS SERIALIZADORES (Para las Cotizaciones) ---

class DetalleCotizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleCotizacion
        fields = ['servicio', 'cantidad', 'precio_unitario']

class CotizacionSerializer(serializers.ModelSerializer):
    # MAGIA: Le decimos que acepte una lista de hijos dentro del padre
    detalles = DetalleCotizacionSerializer(many=True) 

    class Meta:
        model = Cotizacion
        fields = ['id', 'cliente', 'codigo', 'estado', 'fecha_creacion', 'detalles']
        # AQUÍ ESTÁ LA MAGIA: Le quitamos 'estado' a la lista de solo lectura
        read_only_fields = ['compania', 'codigo']

    # Sobreescribimos la función de crear para manejar ambos al mismo tiempo
    def create(self, validated_data):
        # 1. Sacamos la lista de hijos del paquete principal
        detalles_data = validated_data.pop('detalles')
        
        # 2. Generamos un código automático (ej. COT-8492)
        import random
        validated_data['codigo'] = f"COT-{random.randint(1000, 9999)}"
        
        # 3. Guardamos al padre (La Cotización)
        cotizacion = Cotizacion.objects.create(**validated_data)
        
        # 4. Recorremos la lista y guardamos a los hijos pegados al padre
        for detalle in detalles_data:
            DetalleCotizacion.objects.create(cotizacion=cotizacion, **detalle)
        
        return cotizacion