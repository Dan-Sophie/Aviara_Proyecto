from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import TipoDocumento, Rol

Usuario = get_user_model()

class RegistroForm(UserCreationForm):
    nombre_completo = forms.CharField(
        label="Nombre Completo",
        required= True,
        widget = forms.TextInput(attrs={'placeholder': 'Tu nombre y apellido.'})
    )

    tipo_documento = forms.ModelChoiceField(
        queryset= TipoDocumento.objects.all(),
        label ="Tipo de Documento",
        required= True,
        empty_label="Seleccione un Tipo"
    )

    documento = forms.CharField(
        label ="Número de Documento",
        required= True,
        widget = forms.TextInput(attrs={'placeholder': 'Ej: 12345678'})
    )

    telefono = forms.CharField(
        label= "Teléfono",
        required= True,
        max_length=20,
        validators=[RegexValidator(regex=r'^\(\+\d+\)\s?\d+$')],
        help_text ="Formato (+57) 3001234567",
        widget = forms.TextInput(attrs={'placeholder': '(+57) ...'})
    )

    email = forms.EmailField(
        label="Correo Electrónico",
        required= True,
        help_text="Ej: Ingresa tu correo personal (Outlook, Yahoo, Gmail, etc.)"
    )
    
    class Meta:
        model = Usuario
        fields = (
            "username",
            "nombre_completo",
            "tipo_documento",
            "documento",
            "telefono",
            "email"
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado en Aviara.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        nombre = self.cleaned_data.get('nombre_completo')
        if nombre:
            partes = nombre.split(' ', 1)
            user.first_name = partes[0]
            user.last_name = partes[1] if len(partes) > 1 else ''
        if commit:
            user.save()
        return user

class UsuarioForm(forms.ModelForm):
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        required=True,
        label="Rol/Cargo",
        empty_label="Seleccione un cargo",
        widget=forms.Select(attrs={'class': 'form-select', 'style': 'border-radius:12px;'})
    )

    class Meta:
        model = Usuario
        fields = [
            'tipo_documento', 'documento', 'username', 'first_name', 'last_name',
            'email', 'telefono', 'rol', 'password', 'is_staff', 'is_active'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando, forzamos a que el selector muestre el rol actual
        if self.instance and self.instance.pk:
            if self.instance.rol:
                self.fields['rol'].initial = self.instance.rol
            self.fields['password'].required = False

        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'form-control' if field_name != 'rol' else 'form-select',
                    'style': 'border-radius:12px; padding:10px; border: 1px solid #e0e0e0'
                })

    def save(self, commit=True):
        user = super().save(commit=False)
        print(f"VALOR LLEGANDO DEL FORMULARIO: {self.cleaned_data.get('rol')}")
        
        # Guardado manual del Rol (Para que no se resetee a Cliente)
        user.rol = self.cleaned_data.get('rol')
        
        # Guardado manual del estado (Para que no salga Inactivo)
        user.is_active = self.cleaned_data.get('is_active')
        
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user