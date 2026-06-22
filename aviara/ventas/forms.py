from django import forms
from django.forms import inlineformset_factory
from .models import Pedido, DetallePedido, Distribuidor

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['usuario', 'estado_pedido', 'metodo_pago', 'direccion_entrega', 'distribuidor']
        widgets = {
            'direccion_entrega': forms.TextInput(attrs={'placeholder': 'Calle, Carrera, Ciudad...'}),
        }
    def __init(self, *args, **kwargs):
        super(PedidoForm, self).__init__(*args, **kwargs)
        self.fields['distribuidor'].queryset = Distribuidor.objects.all()
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'precio_unitario_venta']

DetallePedidoFormSet = inlineformset_factory(
    Pedido, DetallePedido,
    form = DetallePedidoForm,
    extra=7,    
    can_delete=True
)
