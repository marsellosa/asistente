from django.contrib.admin import *
from prepagos.models import Prepago, Pago
# from socios.models import Socio

class PrepagoAdmin(ModelAdmin):
    # inlines = [PrepagoInline]
    readonly_fields = ['descuento_decimal']
    list_display =  ['socio', 'valor', 'cantidad', 'descuento']

site.register(Prepago, PrepagoAdmin)
site.register(Pago)
