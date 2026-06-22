from django.contrib import admin
from .models import Rol, TipoDocumento, Distribuidor
from django.contrib.auth import get_user_model
from import_export.admin import ImportExportModelAdmin
from import_export import resources

Usuario = get_user_model()

class UsuarioResource(resources.ModelResource):
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')

@admin.register(Usuario)
class UsuarioAdmin(ImportExportModelAdmin):
    resource_class = UsuarioResource
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


admin.site.register(Rol)
admin.site.register(TipoDocumento)
admin.site.register(Distribuidor)
