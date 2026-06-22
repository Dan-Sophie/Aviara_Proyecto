from django.db import models


class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=50, unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_categoria


class Producto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    UNIDAD_CHOICES = [
        ('lb', 'Libra (lb)'),
        ('kg', 'Kilogramo (kg)'),
        ('und', 'Unidad (und)'),
        ('atado', 'Atado'),
        ('500g', '500 gramos'),
        ('250g', '250 gramos'),
    ]
    unidad_medida = models.CharField(max_length=10, choices=UNIDAD_CHOICES, default='lb')
    stock_minimo_global = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock disponible")  # NUEVO
    estado = models.BooleanField(default=True, verbose_name="Activo")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.nombre

    def inhabilitar(self):
        self.estado = False
        self.save()


class Detalle_Agricola(Producto):
    variedad = models.CharField(max_length=100)
    estado_madurez = models.CharField(max_length=50)
    tratamiento = models.TextField()
    humedad_optima = models.CharField(max_length=50)
    fecha_cosecha = models.DateField(null=True, blank=True, verbose_name="Fecha estimada de cosecha")  # NUEVO


class CarritoItem(models.Model):
    """Item temporal en el carrito, vinculado al usuario logueado."""
    from django.conf import settings
    usuario      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carrito')
    producto     = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad     = models.PositiveIntegerField(default=1)
    presentacion = models.CharField(max_length=10, blank=True, default='')  # x6, x15, x30 o vacío
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # precio al momento de agregar
    agregado_en  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'producto', 'presentacion')

    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        pres = f' ({self.presentacion})' if self.presentacion else ''
        return f'{self.producto.nombre}{pres} x{self.cantidad} — {self.usuario}'


class Detalle_Avicola(Producto):
    PRESENTACION_CHOICES = [
        ('x6', 'Media docena (x6)'),
        ('x15', 'Media cubeta (x15)'),
        ('x30', 'Cubeta (x30)'),
    ]
    talla = models.CharField(max_length=20)
    color_huevo = models.CharField(max_length=30)
    tipo_empaque = models.CharField(max_length=50)
    categoria_calidad = models.CharField(max_length=50)
    limpieza = models.BooleanField(default=True)
    presentacion = models.CharField(
        max_length=10,
        choices=PRESENTACION_CHOICES,
        default='x30',
        verbose_name="Presentación"
    )
    precio_x6 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Precio media docena (x6)"
    )
    precio_x15 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Precio media cubeta (x15)"
    )
    precio_x30 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Precio cubeta (x30)"
    )
