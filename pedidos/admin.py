from django.contrib.admin import *
from pedidos.models import *

class PedidoItemInline(StackedInline):
    model = PedidoItem
    extra = 2

class PedidoAdmin(ModelAdmin):
    inlines = [PedidoItemInline]
    readonly_fields = ['pedido_id', 'timestamp', 'updated']
    list_display =  ['pedido_id', 'operador', 'status']
    
class PedidoItemAdmin(ModelAdmin):
    list_display = ['pedido', 'categoria', 'detalles', 'cantidad']

site.register(Pedido, PedidoAdmin)
site.register(PedidoItem, PedidoItemAdmin)
