from django.contrib.admin import *
from prepagos.models import Prepago, Pago

class PrepagoAdmin(ModelAdmin):
    # inlines = [PedidoItemInline]
    readonly_fields = ['descuento_decimal']
    list_display =  ['socio', 'valor', 'cantidad', 'descuento']

site.register(Prepago, PrepagoAdmin)
site.register(Pago)
