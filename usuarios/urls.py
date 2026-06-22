from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),
    path('registro/', views.registro, name='registro'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_sent.html"), name="password_reset_done"),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/carga-masiva/', views.carga_masiva_usuarios, name='carga_masiva_usuarios'),
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('inhabilitar/<int:pk>/', views.inhabilitar_usuario, name='inhabilitar_usuario'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
]