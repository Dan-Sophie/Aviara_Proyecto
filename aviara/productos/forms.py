from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'descripcion', 'precio', 'unidad_medida', 'stock', 'estado']
    
    def clean_precio_venta(self):
        precio = self.cleaned_data.get('precio_venta')
        if precio <= 0:
            raise forms.ValidationError("El precio de venta debe ser mayor a cero.")
        return precio