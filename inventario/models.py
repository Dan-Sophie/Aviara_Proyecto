from django.db import models
from produccion.models import Lote
from django.core.exceptions import ValidationError
from django.conf import settings

class Merma(models.Model):

    ESTADOS_MERMA = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada')
    ]

    MOTIVOS_CHOICES = [
        ('VENCIDO', 'Producto Vencido / Caducado'),
        ('DANO_FISICO', 'Daño Físico / Rotura de empaque'),
        ('MAL_ESTADO', 'Mal Estado / Descomposición'),
        ('CONTEO', 'Discrepancia en Conteo'),
        ('OTRO', 'Otro (Especificar en observaciones)'),
    ]

    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='mermas')
    cantidad_perdida = models.PositiveIntegerField()
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=50, choices=MOTIVOS_CHOICES)
    observaciones = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADOS_MERMA, default='PENDIENTE')
    reportado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='mermas_reportadas')

    def __str__(self):
        return f"Merma {self.id} - {self.lote.codigo_lote} ({self.estado})"
    
    def clean(self):
        super().clean()
        
        # Validación de stock para registros nuevos o existentes que pasen a ser aprobados
        if self.estado == 'APROBADA':
            stock_disponible = self.lote.cantidad_actual
            
            # Si el registro ya existía y ya estaba aprobado, sumamos virtualmente su cantidad original 
            # para saber el stock real antes de esta merma en particular
            if self.pk:
                original = Merma.objects.get(pk=self.pk)
                if original.estado == 'APROBADA':
                    stock_disponible += original.cantidad_perdida
            
            if self.cantidad_perdida > stock_disponible:
                raise ValidationError({
                    'cantidad_perdida': f"No se puede procesar la merma. La cantidad ({self.cantidad_perdida}) "
                                        f"supera el stock actual disponible del lote ({stock_disponible})."
                })
        
    def save(self, *args, **kwargs):
        # Ejecuta validaciones del clean antes de guardar
        self.full_clean()
        
        if not self.pk:
            # ESCENARIO 1: Registro NUEVO que se guarda directamente como APROBADA
            if self.estado == 'APROBADA':
                self.lote.cantidad_actual -= self.cantidad_perdida
                self.lote.save()
        else:
            # Obtener el estado y valores exactos guardados en la Base de Datos antes de este save
            original = Merma.objects.get(pk=self.pk)
            
            if original.estado != 'APROBADA' and self.estado == 'APROBADA':
                # ESCENARIO 2: Pasó de Pendiente/Rechazada a APROBADA (Se descuenta)
                self.lote.cantidad_actual -= self.cantidad_perdida
                self.lote.save()
                
            elif original.estado == 'APROBADA' and self.estado != 'APROBADA':
                # ESCENARIO 3: Estaba APROBADA y cambió a otro estado (Se devuelve el stock al lote)
                self.lote.cantidad_actual += original.cantidad_perdida
                self.lote.save()
                
            elif original.estado == 'APROBADA' and self.estado == 'APROBADA':
                # ESCENARIO 4: Sigue APROBADA pero el usuario modificó la CANTIDAD física de la pérdida
                if original.cantidad_perdida != self.cantidad_perdida:
                    # Devolvemos el valor anterior y restamos el impacto nuevo
                    self.lote.cantidad_actual += original.cantidad_perdida
                    self.lote.cantidad_actual -= self.cantidad_perdida
                    self.lote.save()

        super().save(*args, **kwargs)