from django.urls import path
from . import views

urlpatterns = [
    path('catalogo/',                        views.catalogo_view,        name='catalogo'),
    path('catalogo/api/productos/',          views.api_productos,        name='api_productos'),
    path('catalogo/api/chat/',               views.api_chat,             name='api_chat'),
    # Carrito
    path('carrito/',                         views.carrito_view,         name='carrito'),
    path('carrito/agregar/',                 views.agregar_al_carrito,   name='agregar_carrito'),
    path('carrito/actualizar/<int:item_id>/',views.actualizar_carrito,   name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/',  views.eliminar_del_carrito, name='eliminar_carrito'),
    path('carrito/confirmar/',               views.confirmar_pedido,     name='confirmar_pedido'),
    #Crud Dashboard Administrador
    path('', views.lista_productos, name='lista_productos'),
    path('nuevo/', views.gestionar_producto, name='crear_producto'),
    path('editar/<int:pk>/', views.gestionar_producto, name='editar_producto'),
    path('deshabilitar/<int:pk>/', views.deshabilitar_producto, name='deshabilitar_producto'),
    path('carga-masiva/', views.carga_masiva_productos, name='carga_masiva_productos'),
]

