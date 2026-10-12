from django.contrib import admin
from .models import Pedido,PedidoItem
# Register your models here.
admin.site.register(Pedido)
admin.site.register(PedidoItem)