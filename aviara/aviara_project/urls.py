"""
URL configuration for aviara_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from usuarios import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('', include('usuarios.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('usuarios', include('usuarios.urls')),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_sent.html'), name='password_reset_done'),
    path('produccion/', include('produccion.urls')),
    path('ventas/', include('ventas.urls')),
    path('productos/', include('productos.urls')),   # ← NUEVO
    path('inventario/', include('inventario.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
