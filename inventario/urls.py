from django.urls import path
from . import views

urlpatterns = [
    # =====================================================================
    # SECCIÓN DE MERMAS Y AJUSTES (HU-05)
    # =====================================================================
    # Panel de historial (Deriva internamente a la plantilla de Admin u Operador)
    path('', views.lista_mermas, name='lista_mermas'),
    
    # Formulario de creación (Carga MermaForm o MermaOperadorForm y su HTML correspondiente según el rol)
    path('nuevo/', views.crear_merma, name='crear_merma'),
    
    # Acciones exclusivas del Administrador
    path('aprobar/<int:pk>/', views.aprobar_merma, name='aprobar_merma'),
    path('rechazar/<int:pk>/', views.rechazar_merma, name='rechazar_merma'),
    
    # Endpoint JSON: Retorna los productos/lotes a punto de agotarse al Dashboard
    path('alerta/', views.informar_alerta, name='informar_alerta'),

    # =====================================================================
    # SECCIÓN DE INVENTARIO (Panel General y Reportes)
    # =====================================================================
    # Vista del Administrador (Dashboard completo y descarga PDF)
    path('dashboard/', views.dashboard_inventario, name='dashboard_inventario'),
    path('reporte/pdf/', views.datos_reporte_inventario, name='datos_reporte_inventario'),
]