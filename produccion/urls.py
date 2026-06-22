from django.urls import path
from . import views

urlpatterns = [
    # 📊 Historiales y Tablas Principales
    path('produccion/', views.lista_produccion, name='lista_produccion'),
    path('operador/dashboard/', views.dashboard_operador, name='dashboard_operador'),

    # 🛡️ Rutas de Producción para el Administrador
    path('produccion/crear/admin/', views.registrar_produccion_admin, name='registrar_produccion_admin'),
    path('produccion/editar/<int:pk>/', views.editar_produccion, name='editar_produccion'),

    # 🧑‍🌾 Rutas de Producción para el Operador
    path('produccion/crear/operador/', views.registrar_produccion_operador, name='registrar_produccion_operador'),

    # 🚜 Gestión Compartida de Lotes (Admin y Operador)
    path('lotes/', views.lista_lotes, name='lista_lotes'),
    path('lotes/crear/', views.crear_lote, name='crear_lote'),
    path('lotes/editar/<int:pk>/', views.editar_lote, name='editar_lote'),
]