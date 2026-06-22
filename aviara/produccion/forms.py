from django import forms
from .models import Produccion, Lote

class LoteForm(forms.ModelForm):
    """
    Formulario para la creación y edición de Lotes/Galpones (Solo Administrador).
    """
    class Meta:
        model = Lote
        fields = ['codigo_lote', 'producto', 'cantidad_inicial', 'stock_minimo', 'fecha_produccion', 'fecha_vencimiento', 'estado_calidad', 'esta_activo']
        widgets = {
            'codigo_lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: GALPON-01'}),
            'producto': forms.Select(),
            'cantidad_inicial': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 500'}),
            'stock_minimo': forms.NumberInput(attrs={'placeholder': 'Ej: 50'}),
            'fecha_produccion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'estado_calidad': forms.Select(),
            'esta_activo': forms.CheckboxInput(),
        }


class ProduccionForm(forms.ModelForm):
    """
    Formulario base (Padre) para Administradores.
    Tiene acceso a todos los campos y configuraciones de estilo.
    """
    class Meta:
        model = Produccion
        exclude = ['usuario']
        fields = '__all__'
        widgets = {
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'fecha_produccion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cantidad_recolectada': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 350'}),
            'mortalidad_del_dia': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validación de números positivos para cumplir con la HU-04 (Cantidades No Válidas)
        self.fields['cantidad_recolectada'].min_value = 0
        self.fields['mortalidad_del_dia'].min_value = 0


class ProduccionOperadorForm(ProduccionForm):
    """
    Formulario hijo para Operadores.
    Hereda estilos, pero restringe campos según las Historias de Usuario (HU-04).
    """
    class Meta:
        model = Produccion
        fields = ['lote', 'fecha_produccion', 'cantidad_recolectada', 'mortalidad_del_dia', 'observaciones']
        widgets = ProduccionForm.Meta.widgets

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtramos lotes para que el operador solo vea los activos (Mejor usabilidad)
        self.fields['lote'].queryset = Lote.objects.filter(esta_activo=True)