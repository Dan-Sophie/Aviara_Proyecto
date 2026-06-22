from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .forms import RegistroForm, UsuarioForm
from django.contrib.auth import get_user_model
from import_export.formats.base_formats import XLSX
from .admin import UsuarioResource
from django.db.models import Sum
from datetime import date
from ventas.models import Pedido
from produccion.models import Produccion
from inventario.models import Merma

# Usamos get_user_model() para obtener correctamente tu modelo personalizado de la granja Aviara
Usuario = get_user_model()


def landing(request):
    return render(request, 'landing.html')


@login_required
def home(request):
    user = request.user
    
    # 1. Administrador (Este bloque es el que se está "comiendo" a los demás)
    if user.is_staff or user.is_superuser or user.groups.filter(name__iexact='Administrador').exists():
        hoy = date.today()
        ventas_hoy = Pedido.objects.filter(fecha_pedido=hoy).aggregate(Sum('total_pedido'))['total_pedido__sum'] or 0
        produccion_hoy = Produccion.objects.filter(fecha_produccion=hoy).aggregate(Sum('cantidad_recolectada'))['cantidad_recolectada__sum'] or 0
        mermas_hoy = Merma.objects.filter(fecha_reporte=hoy).aggregate(Sum('cantidad_perdida'))['cantidad_perdida__sum'] or 0
        
        context = {
            'ventas_hoy': ventas_hoy,
            'produccion_hoy': produccion_hoy,
            'mermas_hoy': mermas_hoy,
        }
        return render(request, 'admin/home.html', context)
        
    # 2. Otros roles (Usa los nombres de tus URLs, no las rutas de carpetas)
    elif user.groups.filter(name__iexact='Operador').exists():
        return redirect('dashboard_operador') # <-- Asegúrate que este nombre exista en urls.py
        
    elif user.groups.filter(name__iexact='Distribuidor').exists():
        return redirect('dashboard_distribuidor') # <-- Nombre corregido
    
    # 3. Cliente común (Cualquiera que no sea lo anterior cae aquí)
    else:
        return redirect('perfil_cliente')
    

@login_required
def perfil_cliente(request):
    """Página de perfil del cliente con historial de pedidos."""
    from ventas.models import Pedido
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    return render(request, 'usuarios/perfil_cliente.html', {
        'pedidos': pedidos,
        'usuario': request.user,
    })


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            asunto = '¡ 𝓦𝓮𝓵𝓬𝓸𝓂eke a Aviara !'
            mensaje = f'Hola {user.username}, gracias por registrarte en nuestra pagina de Aviara'
            email_desde = settings.EMAIL_HOST_USER
            email_para = [user.email]

            try:
                send_mail(asunto, mensaje, email_desde, email_para)
            except Exception as e:
                print(f"Error enviando correo: {e}")

            messages.success(request, "Cuenta creada exitosamente.")
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'registration/registro.html', {'form': form})


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('landing')
    return render(request, 'admin/home.html')


@login_required
def lista_usuarios(request):
    # Se eliminó permission_required para evitar el error de base de datos 'auth_user'
    usuarios = Usuario.objects.all().order_by('-date_joined')
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})


@login_required
def carga_masiva_usuarios(request):
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        dataset = UsuarioResource().export()
        nuevo_usuario_resource = UsuarioResource()
        archivo = request.FILES['archivo_excel']

        # Importamos usando el formato XLSX
        dataset.load(archivo.read(), format='xlsx')

        # Validar y guardar
        result = nuevo_usuario_resource.import_data(dataset, dry_run=False)

        if not result.has_errors():
            messages.success(request, f"¡Éxito! Se procesaron los usuarios correctamente.")
        else:
            messages.error(request, "Hubo un error en el formato del archivo.")
        return redirect('lista_usuarios')


@login_required
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Perfil de {usuario.username} actualizado.')
            return redirect('lista_usuarios')
        else:
            print(form.errors)
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})


@login_required
def inhabilitar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario.username == request.user.username:
        messages.error(request, "No puede inhabilitar su propia cuenta.")
        return redirect('lista_usuarios')
        
    usuario.is_active = False
    usuario.save()
    messages.success(request, f"El usuario {usuario.username} ha sido inhabilitado.")
    return redirect('lista_usuarios')

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        
        if form.is_valid():
            # Extraemos el objeto Rol seleccionado (es una instancia del modelo Rol)
            rol_seleccionado = form.cleaned_data.get('rol')
            
            # Comparamos su representación en texto para ver si es administrador
            if rol_seleccionado and str(rol_seleccionado).lower() == 'administrador':
                
                # 🔑 SOLUCIÓN: Pasamos el objeto 'rol_seleccionado' directamente al filtro
                total_admins = Usuario.objects.filter(rol=rol_seleccionado, is_active=True).count()
                
                print(f"--- CANTIDAD ACTUAL DE ADMINS: {total_admins} ---")
                
                if total_admins >= 3:
                    messages.error(request, "⚠️ Registro rechazado: Aviara ya cuenta con el límite máximo permitido (3 administradores activos).")
                    return render(request, 'usuarios/crear_usuario.html', {'form': form})
            
            # Si pasa la validación o no es admin, guarda
            form.save()
            messages.success(request, "Usuario creado con éxito.")
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm()
        
    return render(request, 'usuarios/crear_usuario.html', {'form': form})