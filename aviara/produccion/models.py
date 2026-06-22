from django.db import models
from productos.models import Producto
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

class Lote(models.Model):
    ESTADOS_CALIDAD = [
        ('ACEPTABLE', 'Aceptable'),
        ('MEDIO', 'Medio'),
        ('DAÑADO', 'Dañado'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    codigo_lote = models.CharField(max_length=50, unique=True)
    cantidad_inicial = models.PositiveIntegerField()
    cantidad_actual = models.PositiveIntegerField()
    stock_minimo = models.PositiveIntegerField(default=10)
    fecha_produccion = models.DateField()
    fecha_vencimiento = models.DateField()
    fecha_registro_sistema = models.DateTimeField(auto_now_add=True)
    estado_calidad = models.CharField(max_length=15, choices=ESTADOS_CALIDAD, default='ACEPTABLE')
    esta_activo = models.BooleanField(default=True)
    
    def clean(self):
        super().clean()
        if self.fecha_vencimiento and self.fecha_vencimiento < timezone.now().date():
            raise ValidationError({
                'fecha_vencimiento': 'La fecha de vencimiento debe ser posterior al día de hoy.x'
            })

    def __str__(self):
        return f"Lote {self.codigo_lote} - {self.producto.nombre} ({self.cantidad_actual} und.)"

class Produccion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha_produccion = models.DateField()
    fecha_registro_real = models.DateTimeField(auto_now_add=True)
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='registro_produccion')
    cantidad_recolectada = models.PositiveIntegerField()
    mortalidad_del_dia = models.PositiveIntegerField(default=0)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Registro {self.id} - Lote {self.lote.codigo_lote}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.lote.cantidad_actual += self.cantidad_recolectada
            if self.mortalidad_del_dia >0:
                self.lote.cantidad_actual -= self.mortalidad_del_dia
            self.lote.save()
        super().save(*args, **kwargs)