from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Sum, Count
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta
from productos.models import Producto
from .models import Lote, Merma
from usuarios.models import Usuario
from .forms import MermaForm, MermaOperadorForm
from .utils import generar_pdf
import os
from django.conf import settings

# Función auxiliar para comprobar si es Administrador/Staff
def es_administrador(user):
    return user.is_staff

# =====================================================================
# GESTIÓN DE MERMAS Y AJUSTES (HU-05)
# =====================================================================

@login_required
def lista_mermas(request):
    """Muestra el historial de mermas enrutando correctamente según el rol"""
    if request.user.is_staff:
        # El Administrador ve todas las mermas registradas para gestionar aprobaciones
        mermas = Merma.objects.all().order_by('-fecha_reporte')
        return render(request, 'mermas/merma_list.html', {'mermas': mermas})
    else:
        # El Operador ve únicamente los registros que él mismo ha reportado
        mermas = Merma.objects.filter(reportado_por=request.user).order_by('-fecha_reporte')
        return render(request, 'operador/mermas/lista_mermas.html', {'mermas': mermas})


@login_required
def crear_merma(request):
    if request.method == 'POST':
        form = MermaForm(request.POST) if request.user.is_staff else MermaOperadorForm(request.POST)
        
        if form.is_valid():
            merma = form.save(commit=False)
            merma.reportado_por = request.user
            if not request.user.is_staff:
                merma.estado = 'PENDIENTE'
            merma.save()
            messages.success(request, "El reporte de merma ha sido registrado correctamente.")
            return redirect('lista_mermas')
    else:
        form = MermaForm() if request.user.is_staff else MermaOperadorForm()
        
    # --- RENDERIZADO DIVIDIDO CORREGIDO ---
    if request.user.is_staff:
        return render(request, 'mermas/mermas_crear.html', {'form': form})
    else:
        # Aquí va el render para el operador
        return render(request, 'operador/mermas/form_merma.html', {'form': form})


@login_required
@user_passes_test(es_administrador, login_url='dashboard_inventario')
def aprobar_merma(request, pk):
    """Acción exclusiva del Administrador para autorizar el descuento de inventario"""
    merma = get_object_or_404(Merma, pk=pk)
    if merma.estado == 'PENDIENTE':
        try:
            with transaction.atomic():
                lote = merma.lote
                if lote.cantidad_actual >= merma.cantidad_perdida:
                    lote.cantidad_actual -= merma.cantidad_perdida
                    lote.save()
                    merma.estado = 'APROBADA'
                    merma.save()
                    messages.success(request, f"Merma #{merma.id} aprobada con éxito. Inventario actualizado.")
                else:
                    messages.error(request, f"No se puede aprobar. El lote no tiene stock suficiente ({lote.cantidad_actual} unds disponibles).")
        except Exception as e:
            messages.error(request, f"Error al procesar la aprobación: {str(e)}")
    return redirect('lista_mermas')


@login_required
@user_passes_test(es_administrador, login_url='dashboard_inventario')
def rechazar_merma(request, pk):
    """Acción exclusiva del Administrador para invalidar el ajuste (HU-05 Escenario 3)"""
    merma = get_object_or_404(Merma, pk=pk)
    if merma.estado == 'PENDIENTE':
        merma.estado = 'RECHAZADA'
        merma.save()
        messages.warning(request, f"El reporte de merma #{merma.id} ha sido rechazado.")
    return redirect('lista_mermas')


@login_required
def informar_alerta(request):
    """Endpoint JSON que retorna los lotes que están a punto de agotarse"""
    # Buscamos los lotes que tengan pocas unidades (menos de 10) y que no estén en 0
    lotes_criticos = Lote.objects.filter(cantidad_actual__gt=0, cantidad_actual__lte=10)
    
    alertas = [
        {
            "id": lote.id,
            "codigo": lote.codigo_lote,
            "cantidad": lote.cantidad_actual,
            "mensaje": f"El lote {lote.codigo_lote} está críticamente bajo de stock ({lote.cantidad_actual} unds)."
        }
        for lote in lotes_criticos
    ]
    
    return JsonResponse({"alertas": alertas})

def dashboard_inventario(request):
    return render(request, 'inventario/inventario_dashboard.html')
# =====================================================================
# GESTIÓN DE INVENTARIO (Panel General y Reportes)
# =====================================================================

def datos_reporte_inventario(request):
    ahora = timezone.now()
    inicio_mes = ahora.replace(day=1)
    
    # 1. Cálculos de datos
    productos_estado = Producto.objects.values('estado').annotate(total=Count('id'))
    mermas_mes = Merma.objects.filter(fecha_reporte__gte=inicio_mes)
    resumen_mermas = mermas_mes.values('motivo').annotate(
        total_cantidad=Sum('cantidad_perdida'),
        conteo=Count('id')
    )
    top_usuario = Merma.objects.values('reportado_por__username').annotate(
        total_mermas=Count('id')
    ).order_by('-total_mermas').first()
    lotes_afectados = Merma.objects.values('lote__id').distinct().count()

    # 2. Definición del contexto (Aquí es donde se define 'context')
    context = {
        'productos': productos_estado,
        'mermas_mes': resumen_mermas,
        'top_usuario': top_usuario,
        'lotes_afectados': lotes_afectados,
    }
    
    # 3. Generar el PDF (Todo esto debe estar DENTRO de la función)
    pdf_path = generar_pdf('inventario/reporte_pdf.html', context, 'reporte_inventario.pdf')
    
    return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')