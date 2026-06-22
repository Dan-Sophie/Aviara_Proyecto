from django import forms
from .models import Merma
from produccion.models import Lote

class MermaForm(forms.ModelForm):
    class Meta:
        model = Merma
        fields = ['lote', 'cantidad_perdida', 'motivo', 'observaciones']
        widgets = {
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_perdida': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 15'}),
            'motivo': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Detalles para la revisión...'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cantidad_perdida'].min_value = 1
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['observaciones'].required = True


class MermaOperadorForm(forms.ModelForm):
    class Meta:
        model = Merma
        fields = ['lote', 'cantidad_perdida', 'motivo', 'observaciones']
        # Esto le dice a Django: "Usa el widget Select automáticamente por tener choices en el modelo"
        widgets = {
            'motivo': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lote'].queryset = Lote.objects.filter(esta_activo=True)
        self.fields['observaciones'].required = True
        # Aseguramos que el select tenga el primer elemento vacío si lo deseas
        self.fields['motivo'].empty_label = "--- Seleccione el motivo ---"