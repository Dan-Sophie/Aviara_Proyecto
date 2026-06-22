import json
import csv
import io
import requests
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Producto, Categoria, CarritoItem
from .forms import ProductoForm


def catalogo_view(request):
    """Vista principal del catálogo."""
    from .models import Detalle_Avicola
    productos = list(Producto.objects.filter(estado=True).select_related('categoria'))
    categorias = Categoria.objects.filter(estado=True)

    # Mapear precios de presentación avícola por pk
    avicola_map = {
        av.pk: av
        for av in Detalle_Avicola.objects.filter(estado=True)
    }

    # Anotar cada producto con sus precios de presentación
    for p in productos:
        av = avicola_map.get(p.pk)
        if av:
            p.precio_x6_val  = av.precio_x6  or ''
            p.precio_x15_val = av.precio_x15 or ''
            p.precio_x30_val = av.precio_x30 or ''
        else:
            p.precio_x6_val  = ''
            p.precio_x15_val = ''
            p.precio_x30_val = ''

    return render(request, 'productos/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'carrito_count': CarritoItem.objects.filter(usuario=request.user).count() if request.user.is_authenticated else 0,
    })


def api_productos(request):
    """Endpoint JSON para búsqueda en tiempo real."""
    query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '')

    productos = Producto.objects.filter(estado=True).select_related('categoria')

    if query:
        productos = productos.filter(nombre__icontains=query) | \
                    productos.filter(descripcion__icontains=query)

    if categoria_id:
        productos = productos.filter(categoria__id=categoria_id)

    data = []
    for p in productos:
        data.append({
            'id': p.id,
            'nombre': p.nombre,
            'descripcion': p.descripcion,
            'precio': str(p.precio),
            'unidad_medida': p.unidad_medida,
            'categoria': p.categoria.nombre_categoria if p.categoria else '',
            'imagen': p.imagen.url if p.imagen else None,
        })

    return JsonResponse({'productos': data})


@csrf_exempt
def api_chat(request):
    """Endpoint del chatbot usando Groq API."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        body = json.loads(request.body)
        mensaje_usuario = body.get('mensaje', '').strip()
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Datos inválidos'}, status=400)

    if not mensaje_usuario:
        return JsonResponse({'error': 'Mensaje vacío'}, status=400)

    # Obtener productos para dar contexto al chatbot
    productos = Producto.objects.filter(estado=True).select_related('categoria')
    lista_productos = "\n".join([
        f"- {p.nombre} ({p.categoria.nombre_categoria if p.categoria else 'Sin categoría'}): "
        f"${p.precio} por {p.unidad_medida}. {p.descripcion[:100]}"
        for p in productos[:30]
    ])

    # Contexto de pedidos del usuario si está logueado
    contexto_usuario = ""
    if request.user.is_authenticated:
        try:
            from ventas.models import Pedido
            pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')[:5]
            if pedidos:
                lineas = []
                for p in pedidos:
                    detalles = ", ".join([
                        f"{d.producto.nombre} x{d.cantidad}"
                        for d in p.detalles.all()
                    ])
                    lineas.append(
                        f"- Pedido #{p.id} ({p.get_estado_pedido_display()}) "
                        f"el {p.fecha_pedido.strftime('%d/%m/%Y')}: {detalles}. "
                        f"Total: ${p.total_pedido}"
                    )
                contexto_usuario = f"\n\nEl cliente que te habla es {request.user.get_full_name() or request.user.username}. Sus últimos pedidos son:\n" + "\n".join(lineas)
            else:
                contexto_usuario = f"\n\nEl cliente que te habla es {request.user.get_full_name() or request.user.username} y aún no tiene pedidos."
        except Exception:
            pass

    system_prompt = f"""Eres un asistente virtual de Aviara, una empresa colombiana que produce 
y vende productos avícolas (huevos, pollos) y agrícolas frescos.
Eres amable, hablas en español colombiano informal, y ayudas a los clientes a conocer 
los productos, precios y a realizar pedidos.

Estos son los productos disponibles actualmente:
{lista_productos}
{contexto_usuario}

Responde de forma breve y útil. Si el cliente pregunta por un producto que no está en 
la lista, dile amablemente que por ahora no está disponible. 
No inventes precios ni información que no esté en la lista.
Si el cliente pregunta por sus pedidos, usa la información de sus pedidos para responder."""

    try:
        groq_api_key = getattr(settings, 'GROQ_API_KEY', '')
        if not groq_api_key:
            return JsonResponse({'respuesta': 'El chatbot no está configurado aún. Por favor contacte al administrador.'})

        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {groq_api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'llama-3.3-70b-versatile',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': mensaje_usuario},
                ],
                'max_tokens': 300,
                'temperature': 0.7,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        respuesta = data['choices'][0]['message']['content']
        return JsonResponse({'respuesta': respuesta})

    except requests.exceptions.Timeout:
        return JsonResponse({'respuesta': 'Lo siento, tardé demasiado en responder. ¡Intenta de nuevo!'})
    except Exception as e:
        return JsonResponse({'respuesta': 'Hubo un error al procesar tu mensaje. ¡Intenta de nuevo!'})


# ─────────────────────────────────────────────
# CARRITO
# ─────────────────────────────────────────────

@login_required(login_url='login')
def carrito_view(request):
    """Página del carrito del usuario logueado."""
    items = CarritoItem.objects.filter(usuario=request.user).select_related('producto__categoria')
    total = sum(item.subtotal() for item in items)
    return render(request, 'productos/carrito.html', {
        'items': items,
        'total': total,
    })


@csrf_exempt
@login_required(login_url='login')
def agregar_al_carrito(request):
    """Agrega o actualiza un ítem en el carrito. Requiere login."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        body         = json.loads(request.body)
        producto_id  = int(body.get('producto_id'))
        cantidad     = int(body.get('cantidad', 1))
        presentacion = body.get('presentacion', '').strip()  # x6, x15, x30 o ''
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Datos inválidos'}, status=400)

    producto = get_object_or_404(Producto, pk=producto_id, estado=True)

    # Determinar precio según presentación
    precio = producto.precio
    if presentacion:
        from .models import Detalle_Avicola
        try:
            av = Detalle_Avicola.objects.get(pk=producto_id)
            precio_pres = {'x6': av.precio_x6, 'x15': av.precio_x15, 'x30': av.precio_x30}.get(presentacion)
            if precio_pres:
                precio = precio_pres
        except Detalle_Avicola.DoesNotExist:
            pass

    # Validar cantidad máxima (máximo stock disponible)
    max_cantidad = producto.stock
    if cantidad < 1:
        cantidad = 1
    if cantidad > max_cantidad:
        return JsonResponse({'error': f'Stock máximo disponible: {max_cantidad}'}, status=400)

    item, created = CarritoItem.objects.update_or_create(
        usuario=request.user,
        producto=producto,
        presentacion=presentacion,
        defaults={'cantidad': cantidad, 'precio_unitario': precio},
    )

    total_carrito = sum(i.subtotal() for i in CarritoItem.objects.filter(usuario=request.user))
    cant_items    = CarritoItem.objects.filter(usuario=request.user).count()

    return JsonResponse({
        'ok': True,
        'creado': created,
        'subtotal': float(item.subtotal()),
        'total_carrito': float(total_carrito),
        'cant_items': cant_items,
    })


@csrf_exempt
@login_required(login_url='login')
def actualizar_carrito(request, item_id):
    """Actualiza la cantidad de un ítem del carrito."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    item = get_object_or_404(CarritoItem, pk=item_id, usuario=request.user)

    try:
        body     = json.loads(request.body)
        cantidad = int(body.get('cantidad', 1))
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Datos inválidos'}, status=400)

    if cantidad < 1:
        item.delete()
        accion = 'eliminado'
    elif cantidad > item.producto.stock:
        return JsonResponse({'error': f'Stock máximo: {item.producto.stock}'}, status=400)
    else:
        item.cantidad = cantidad
        item.save()
        accion = 'actualizado'

    total_carrito = sum(i.subtotal() for i in CarritoItem.objects.filter(usuario=request.user))
    cant_items    = CarritoItem.objects.filter(usuario=request.user).count()

    return JsonResponse({
        'ok': True,
        'accion': accion,
        'subtotal': float(item.subtotal()) if accion != 'eliminado' else 0,
        'total_carrito': float(total_carrito),
        'cant_items': cant_items,
    })


@csrf_exempt
@login_required(login_url='login')
def eliminar_del_carrito(request, item_id):
    """Elimina un ítem del carrito."""
    item = get_object_or_404(CarritoItem, pk=item_id, usuario=request.user)
    item.delete()
    total_carrito = sum(i.subtotal() for i in CarritoItem.objects.filter(usuario=request.user))
    cant_items    = CarritoItem.objects.filter(usuario=request.user).count()
    return JsonResponse({'ok': True, 'total_carrito': float(total_carrito), 'cant_items': cant_items})


@login_required(login_url='login')
def confirmar_pedido(request):
    """Convierte el carrito en un Pedido real y descuenta stock."""
    from ventas.models import Pedido, DetallePedido

    items = CarritoItem.objects.filter(usuario=request.user).select_related('producto')
    if not items.exists():
        return redirect('carrito')

    if request.method == 'POST':
        direccion    = request.POST.get('direccion', '').strip()
        telefono     = request.POST.get('telefono', '').strip()
        metodo_pago  = request.POST.get('metodo_pago', 'efectivo').strip()

        if not direccion:
            items_list = list(items)
            total = sum(i.subtotal() for i in items_list)
            return render(request, 'productos/carrito.html', {
                'items': items_list,
                'total': total,
                'error': 'La dirección de entrega es obligatoria.',
                'mostrar_pago': True,
            })

        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            direccion_entrega=direccion,
            metodo_pago=metodo_pago,
            total_pedido=0,
        )

        # Crear detalles y descontar stock
        for item in items:
            DetallePedido.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario_venta=item.precio_unitario,
                presentacion=item.presentacion,
            )
            # Descontar stock — para huevos el factor multiplica según presentación
            factor = {'x6': 6, 'x15': 15, 'x30': 30}.get(item.presentacion, 1)
            item.producto.stock = max(0, item.producto.stock - (item.cantidad * factor))
            item.producto.save(update_fields=['stock'])

        pedido.actualizar_total()

        # Vaciar carrito
        items.delete()

        return render(request, 'productos/pedido_confirmado.html', {'pedido': pedido})

    # GET → mostrar formulario de pago
    items_list = list(items)
    total = sum(i.subtotal() for i in items_list)
    return render(request, 'productos/carrito.html', {
        'items': items_list,
        'total': total,
        'mostrar_pago': True,
    })

#CRUD'S PRODUCTOS DASHBOARD ADMINISTRADOR

def lista_productos(request):
    productos = Producto.objects.all().order_by('categoria', 'nombre')
    return render(request, 'productos/producto_list.html', {'productos': productos})

def gestionar_producto(request, pk=None):
    producto = get_object_or_404(Producto, pk=pk) if pk else None

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            prod_guardado = form.save()
            messages.success(request, f"Producto '{prod_guardado.nombre}' guardado con éxito.")
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/producto_form.html', {
        'form': form,
        'producto': producto
    })

def deshabilitar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.estado = False
    producto.save()
    messages.success(request, f"Producto '{producto.nombre}' deshabilitado del catálogo.")
    return redirect('lista_productos')

def carga_masiva_productos(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']

        if archivo.name.endswith('.csv'):
            data_set = archivo.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string) #Omitir lista de encabezados del archivo csv

            contador_creador = 0
            for row in csv.reader(io_string, delimiter=','):
                if row:
                    Producto.objects.create(
                        nombre = row[0],
                        categoria = row[1],
                        descripcion = row[2],
                        precio = float(row[3]),
                        cantidad = int(row[4]),
                        estado = True
                    )
                    contador_creados +=1
            messages.success(request, f"Se cargaron con éxito {contador_creados} productos nuevos al catálogo.")
        else:
            messages.error(request, "Por el momento el sistema solo procesa archivos planos .csv con codificación estándar.")
    return redirect('lista_productos')
        