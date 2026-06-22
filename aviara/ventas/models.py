from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from productos.models import Producto
from usuarios.models import Distribuidor

class Pedido(models.Model):
        ESTADOS_PEDIDO = [
            ('PENDIENTE', 'Pendiente'),
            ('PROCESANDO', 'En Proceso'),
            ('CAMINO', 'En Camino'),
            ('ENTREGADO', 'Entregado'),
            ('CANCELADO', 'Cancelado'),
        ]
        usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
        fecha_pedido = models.DateTimeField(auto_now_add=True)
        estado_pedido = models.CharField(max_length=50, choices=ESTADOS_PEDIDO, default='PENDIENTE')
        metodo_pago = models.CharField(max_length=50)
        direccion_entrega = models.CharField(max_length=255)
        total_pedido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
        distribuidor = models.ForeignKey(Distribuidor, on_delete=models.SET_NULL, null=True, blank=True)    
        fecha_despacho = models.DateTimeField(null=True, blank=True)
        fecha_entrega_real = models.DateTimeField(null=True, blank=True)
        novedad_entrega = models.TextField(null=True, blank=True)

        def __str__(self):
            return f"Pedido {self.id} - {self.usuario.get_full_name()} ({self.get_estado_pedido_display()})"
        
        def clean(self):
            if self.pk:
                original = Pedido.objects.get(pk=self.pk)
                if original.estado_pedido == 'CAMINO' and self.estado_pedido == 'CANCELADO':
                    raise ValidationError("No se puede calcular un pedido que ya está en camino.")
        
        def actualizar_total(self):
            total = sum(detalle.subtotal for detalle in self.detalles.all())
            self.total_pedido = total
            self.save()

class DetallePedido(models.Model):
        pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
        producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
        cantidad = models.PositiveIntegerField() 
        presentacion = models.CharField(max_length=10, blank=True, default='', verbose_name='Presentación (x6/x15/x30)')
        precio_unitario_venta = models.DecimalField(max_digits=10, decimal_places=2)
        subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

        def clean(self):
            if self.producto_id:  # Usamos _id para verificar la existencia del valor en DB
                # Ahora sí, podemos acceder al objeto producto de forma segura
                producto_obj = self.producto
                
                cantidad_anterior = 0
                if self.pk:
                    try:
                        detalle_original = DetallePedido.objects.get(pk=self.pk)
                        cantidad_anterior = detalle_original.cantidad
                    except DetallePedido.DoesNotExist:
                        cantidad_anterior = 0
                
                stock_disponible_real = producto_obj.stock + cantidad_anterior
                
                if self.cantidad > stock_disponible_real:
                    raise ValidationError(
                        f"No hay suficiente stock para '{producto_obj.nombre}'. "
                        f"Disponible real: {producto_obj.stock}"
                    )
            else:
                # Si no hay producto, quizás quieras lanzar otro error o simplemente omitir
                raise ValidationError("Debes seleccionar un producto.")
        
        def save(self, *args, **kwargs):
            if self.cantidad and self.precio_unitario_venta:
                self.subtotal = self.cantidad * self.precio_unitario_venta
            else:
                self.subtotal=0
            super().save(*args, **kwargs)


class EvidenciaEntrega(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='evidencia')
    foto_comprobante = models.ImageField(upload_to='evidencias/')
    firma_digital = models.ImageField(upload_to='firmas/', null=True, blank=True)
    fecha_hora_evidencia = models.DateTimeField(auto_now_add=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Evidencia Pedido {self.pedido.id}"