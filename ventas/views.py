from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Sum, Count
from .models import Pedido, Distribuidor
from .forms import PedidoForm, DetallePedidoFormSet
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db.models import Q

def es_admin_o_distribuidor(user):
    return user.is_staff or user.groups.filter(name='Distribuidor').exists()

@login_required
@user_passes_test(es_admin_o_distribuidor, login_url='login')
def lista_pedidos(request):
    """
    Función unificada para la ruta principal de ventas.
    """
    # 1. SI ES ADMINISTRADOR: Ve el panel general de control de pedidos
    if request.user.is_staff:
        estado_filtro = request.GET.get('estado', None)

        if estado_filtro:
            pedidos = Pedido.objects.filter(estado_pedido=estado_filtro).order_by('-fecha_pedido')
        else:
            pedidos = Pedido.objects.all().order_by('-fecha_pedido')
        
        context = {
            'pedidos': pedidos,
            'pedidos_pendientes_count': Pedido.objects.filter(estado_pedido='PENDIENTE').count(),
            'pedidos_entregados_count': Pedido.objects.filter(estado_pedido='ENTREGADO').count(),
            'total_ventas': Pedido.objects.filter(estado_pedido='ENTREGADO').aggregate(total=Sum('total_pedido'))['total'] or 0,
        }
        return render(request, 'ventas/lista_pedidos.html', context)
        
    # 2. SI ES DISTRIBUIDOR (Sarita): Ve su dashboard de entregas
    else:
        pedidos_pendientes = Pedido.objects.filter(estado_pedido='EN_CAMINO').order_by('fecha_pedido')
        pedidos_entregados = Pedido.objects.filter(estado_pedido='ENTREGADO').order_by('-fecha_pedido')

        context = {
            'pedidos_pendientes': pedidos_pendientes,
            'pedidos_entregados': pedidos_entregados,
            'conteo_pendientes': pedidos_pendientes.count(),
            'conteo_entregados': pedidos_entregados.count(),
        }
        return render(request, 'distribuidor/distribuidor_dashboard.html', context)


def gestionar_pedido(request, pk=None):
    pedido = get_object_or_404(Pedido, pk=pk) if pk else None

    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        formset = DetallePedidoFormSet(request.POST, instance=pedido)

        if form.is_valid() and formset.is_valid():
            pedido_guardado = form.save()
            detalles = formset.save(commit=False)
            for detalle in detalles:
                detalle.pedido = pedido_guardado
                detalle.save()
            pedido_guardado.refresh_from_db()
            pedido_guardado.actualizar_total()
            messages.success(request, f"Pedido #{pedido_guardado.id} guardado correctamente.")
            return redirect('lista_pedidos')
        else:
            error_texto = f"Error: {form.errors} | Detalles: {formset.errors}"
            messages.error(request, error_texto)
    else:
        form = PedidoForm(instance=pedido)
        formset = DetallePedidoFormSet(instance=pedido)
    
    # ESTE RETURN ES OBLIGATORIO: Siempre se ejecutará si falla el POST o si es un GET
    return render(request, 'ventas/pedido_form.html', {
        'form': form,
        'formset': formset,
        'pedido': pedido
    })


def detalle_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    return render(request, 'ventas/pedido_detalle.html', {
        'pedido': pedido
    })


def cambiar_estado_pedido(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    if request.method == 'POST':
        # Aquí guardas la foto del comprobante
        archivo = request.FILES.get('comprobante')
        if archivo:
            pedido.estado_pedido = 'ENTREGADO'
            # Asumiendo que tienes un campo 'evidencia' en tu modelo
            pedido.evidencia = archivo 
            pedido.save()
            # Agregar mensaje de éxito
            return redirect('dashboard_distribuidor')
        else:
            # Aquí disparas el error si no hay archivo (HU-02)
            messages.error(request, "Registro inválido. No se encontró archivo de comprobante.")
            return redirect('dashboard_distribuidor')


@login_required
def dashboard_distribuidor(request):
    # 1. Obtener distribuidor
    try:
        perfil = Distribuidor.objects.get(usuario=request.user)
    except Distribuidor.DoesNotExist:
        return render(request, 'distribuidor/distribuidor_dashboard.html', {'conteo_pendientes': 0})

    # 2. Filtrar usando el ID del perfil que ya sabemos que funciona
    pedidos = Pedido.objects.filter(distribuidor_id=perfil.id)
    
    # 3. Separar estados
    pedidos_pendientes = pedidos.filter(estado_pedido__in=['PENDIENTE', 'CAMINO'])
    
    return render(request, 'distribuidor/distribuidor_dashboard.html', {
        'pedidos_pendientes': pedidos_pendientes,
        'conteo_pendientes': pedidos_pendientes.count(),
    })

