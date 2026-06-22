from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto, Detalle_Agricola, Detalle_Avicola


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre_categoria', 'estado')
    list_editable = ('estado',)
    search_fields = ('nombre_categoria',)


class ProductoBaseAdmin(admin.ModelAdmin):
    """Configuración base compartida para todos los tipos de producto."""
    list_display = ('nombre', 'categoria', 'precio', 'unidad_medida', 'stock', 'estado', 'vista_imagen')
    list_editable = ('precio', 'unidad_medida', 'stock', 'estado')
    list_filter = ('categoria', 'estado')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('vista_imagen',)

    def vista_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="height:50px; border-radius:6px;" />', obj.imagen.url)
        return '—'
    vista_imagen.short_description = 'Imagen'


@admin.register(Detalle_Avicola)
class DetalleAvicolaAdmin(ProductoBaseAdmin):
    list_display = ProductoBaseAdmin.list_display + ('talla', 'color_huevo', 'presentacion')
    fieldsets = (
        ('Información general', {
            'fields': ('nombre', 'descripcion', 'categoria', 'precio', 'unidad_medida', 'stock', 'stock_minimo_global', 'estado', 'imagen', 'vista_imagen')
        }),
        ('Precios por presentación', {
            'description': 'Deja en blanco las presentaciones que no apliquen.',
            'fields': ('precio_x6', 'precio_x15', 'precio_x30'),
        }),
        ('Detalles avícolas', {
            'fields': ('talla', 'color_huevo', 'tipo_empaque', 'categoria_calidad', 'limpieza', 'presentacion')
        }),
    )


@admin.register(Detalle_Agricola)
class DetalleAgricolaAdmin(ProductoBaseAdmin):
    list_display = ProductoBaseAdmin.list_display + ('variedad', 'fecha_cosecha')
    fieldsets = (
        ('Información general', {
            'fields': ('nombre', 'descripcion', 'categoria', 'precio', 'unidad_medida', 'stock', 'stock_minimo_global', 'estado', 'imagen', 'vista_imagen')
        }),
        ('Detalles agrícolas', {
            'fields': ('variedad', 'estado_madurez', 'tratamiento', 'humedad_optima', 'fecha_cosecha')
        }),
    )


@admin.register(Producto)
class ProductoAdmin(ProductoBaseAdmin):
    fieldsets = (
        ('Información general', {
            'fields': ('nombre', 'descripcion', 'categoria', 'precio', 'unidad_medida', 'stock', 'stock_minimo_global', 'estado', 'imagen', 'vista_imagen')
        }),
    )
