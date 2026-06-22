from django.db import models
from django.contrib.auth.models import AbstractUser

class Rol(models.Model):
    nombre_rol = models.CharField(max_length=50, unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_rol

class TipoDocumento(models.Model):
    nombre_tipo = models.CharField(max_length=50, unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_tipo

class Usuario(AbstractUser):
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT, null=True)
    documento = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=20, default='Activo')

    def __str__(self):
        return f"{self.username} - ({self.rol})"

class Distribuidor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_distribuidor')
    tipo_vehiculo = models.CharField(max_length=50)
    placa_vehiculo = models.CharField(max_length=10, unique=True)
    numero_licencia = models.CharField(max_length=20, unique=True)
    disponibilidad = models.BooleanField(default=True)

    def __str__(self):
        return f"Distribuidor: {self.usuario.get_full_name()} - ({self.placa_vehiculo})"