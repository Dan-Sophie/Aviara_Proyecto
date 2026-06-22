from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home/', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
    path('reset_password/', 
     auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name="password_reset"),
]