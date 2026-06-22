from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pedidos, name='lista_pedidos'),
    path('nuevo/', views.gestionar_pedido, name='crear_pedido'),
    path('editar/<int:pk>/', views.gestionar_pedido, name='editar_pedido'),
    path('detalle/<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedido/finalizar/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('mi-dashboard/', views.dashboard_distribuidor, name='dashboard_distribuidor'),
]