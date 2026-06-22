from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Produccion, Lote
from productos.models import Producto
from .forms import LoteForm, ProduccionForm, ProduccionOperadorForm
import datetime

# =====================================================================
# 🛡️ REGLAS DE SEGURIDAD Y ROLES
# =====================================================================

def es_administrador(user):
    """Devuelve True si el usuario tiene permisos de Staff (Administrador)."""
    return user.is_staff


# =====================================================================
# 📦 GESTIÓN DE HISTORIALES (Lectura de Datos)
# =====================================================================

@login_required
def lista_produccion(request):
    """
    Muestra el historial de producción discriminando la interfaz según el rol.
    Solo lee datos, no procesa ningún formulario.
    """
    if request.user.is_staff:
        # Administrador: Ve todo el panorama global de la granja
        registros = Produccion.objects.all().select_related('lote', 'usuario').order_by('-fecha_produccion')
        return render(request, 'produccion/lista.html', {'registros': registros})
    else:
        # Operador: Solo visualiza sus propias recolecciones diarias
        registros = Produccion.objects.filter(usuario=request.user).select_related('lote').order_by('-fecha_produccion')
        return render(request, 'operador/produccion/lista_produccion.html', {'registros': registros})


# =====================================================================
# 🛠️ FLUJO EXCLUSIVO DEL ADMINISTRADOR GENERAL
# =====================================================================

@login_required
@user_passes_test(es_administrador, login_url='dashboard_operador')
def registrar_produccion_admin(request):
    """
    CREACIÓN ADMIN: Permite registrar producciones asignándolas a cualquier operador.
    Usa 'ProduccionForm' (incluye el selector completo de usuarios).
    """
    if request.method == 'POST':
        form = ProduccionForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda directo porque el Admin selecciona manualmente el usuario en el formulario
            messages.success(request, "¡Registro Administrativo Exitoso! Los datos se han sumado al Stock.")
            return redirect('lista_produccion')
        else:
            messages.error(request, "Por favor, llene todos los campos obligatorios.")
    else:
        form = ProduccionForm()
        
    # Inyección estética de clases de Tailwind para los inputs de administración
    clase_input_tailwind = (
        "w-full p-3 bg-gray-50 border border-gray-200 rounded-xl outline-none "
        "focus:ring-2 focus:ring-[#107B4F] focus:bg-white transition duration-200"
    )
    for field_name, field in form.fields.items():
        field.widget.attrs.update({'class': clase_input_tailwind})
        
    return render(request, 'produccion/form_produccion.html', {
        'form': form, 
        'titulo': 'Registrar Producción Ejecutiva'
    })


@login_required
@user_passes_test(es_administrador, login_url='dashboard_operador')
def editar_produccion(request, pk):
    """
    EDICIÓN ADMIN: Permite corregir errores de inventario de cualquier registro viejo.
    """
    produccion = get_object_or_404(Produccion, pk=pk)
    
    if request.method == 'POST':
        form = ProduccionForm(request.POST, instance=produccion)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.usuario = request.user
            registro.save()
            messages.success(request, f"¡Modificación exitosa! El registro del lote {produccion.lote.codigo_lote} ha sido actualizado.")
            return redirect('lista_produccion')
        else:
            messages.error(request, f"Error en validación: {form.errors}")  
    else:
        form = ProduccionForm(instance=produccion)
    
    # Inyección estética de clases de Tailwind
    clase_input_tailwind = (
        "w-full p-3 bg-gray-50 border border-gray-200 rounded-xl outline-none "
        "focus:ring-2 focus:ring-[#107B4F] focus:bg-white transition duration-200"
    )
    for field_name, field in form.fields.items():
        field.widget.attrs.update({'class': clase_input_tailwind})
        
    return render(request, 'produccion/editar_produccion.html', {
        'form': form,
        'produccion': produccion, 
        'titulo': f'Panel de Edición - Lote {produccion.lote.codigo_lote}'
    })


# =====================================================================
# 🧑‍🌾 FLUJO EXCLUSIVO DEL OPERADOR DE CAMPO
# =====================================================================

@login_required
def registrar_produccion_operador(request):
    """CREACIÓN OPERADOR: Formulario rápido para el trabajador en los galpones."""
    if request.method == 'POST':
        form = ProduccionOperadorForm(request.POST)
        if form.is_valid():
            produccion = form.save(commit=False)
            produccion.usuario = request.user
            produccion.save()
            messages.success(request, "¡Registro Exitoso! Tu recolección diaria ha sido guardada.")
            return redirect('lista_produccion')
        else:
            messages.error(request, "Por favor, llene todos los campos para asegurar el registro.")
    else:
        form = ProduccionOperadorForm()
        
    # 🌟 Cambiamos el destino al nuevo archivo exclusivo del operador:
    return render(request, 'operador/produccion/form_produccion_operador.html', {
        'form': form,
        'titulo': 'Registrar Producción Diaria'
    })

@login_required
def dashboard_operador(request):
    """Panel de Control resumido con métricas diarias para el operador de campo."""
    hoy = datetime.date.today()
    lotes_activos = Lote.objects.filter(esta_activo=True)
    
    recolecciones_del_dia = Produccion.objects.filter(
        usuario=request.user, 
        fecha_produccion=hoy
    ).count()
    
    context = {
        'lotes_activos_conteo': lotes_activos.count(),
        'fecha_hoy': hoy, 
        'recolecciones_hoy': recolecciones_del_dia,
        'alertas_calidad': lotes_activos.filter(estado_calidad='DAÑADO').count(),
    }
    return render(request, 'operador/operador_dashboard.html', context)


# =====================================================================
# 🚜 GESTIÓN DE LOTES (Acceso para Administrador y Operador)
# =====================================================================

@login_required
def lista_lotes(request):
    """Muestra la lista de lotes activos para cualquier miembro del equipo."""
    lotes = Lote.objects.filter(esta_activo=True).order_by('-fecha_registro_sistema')
    return render(request, 'produccion/lista_lote.html', {'lotes': lotes})


@login_required
def crear_lote(request):
    """Permite tanto al Admin como al Operador abrir un nuevo frente de producción."""
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            lote = form.save(commit=False)
            lote.cantidad_actual = lote.cantidad_inicial
            lote.save()
            messages.success(request, f"Lote {lote.codigo_lote} creado con éxito.")
            return redirect('lista_lotes')
    else:
        form = LoteForm()
    return render(request, 'produccion/form_lote.html', {'form': form, 'titulo': 'Nuevo Lote'})


@login_required
def editar_lote(request, pk):
    """Permite actualizar parámetros o estado de sanidad de los lotes."""
    lote = get_object_or_404(Lote, pk=pk)
    if request.method == 'POST':
        form = LoteForm(request.POST, instance=lote)
        if form.is_valid():
            form.save()
            messages.info(request, "Información del lote actualizada.")
            return redirect('lista_lotes')
    else:
        form = LoteForm(instance=lote)
    return render(request, 'produccion/form_lote.html', {'form': form, 'titulo': 'Editar Lote'})