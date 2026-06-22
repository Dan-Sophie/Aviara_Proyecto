from django.contrib import admin
from .models import Pedido, DetallePedido, EvidenciaEntrega

admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(EvidenciaEntrega)
