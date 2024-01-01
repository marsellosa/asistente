from django.contrib.admin import * #type: ignore
from prepagos.models import Prepago, Pago
# from socios.models import Socio

class PagoInline(StackedInline):
    model = Pago
    extra = 1

class PrepagoAdmin(ModelAdmin):
    inlines = [PagoInline]
    readonly_fields = ['descuento_decimal']
    list_display =  ['socio', 'valor', 'cantidad', 'descuento']

class PagoAdmin(ModelAdmin):
    list_display = ['get_nombre_socio', 'monto', 'usuario', 'fecha']

site.register(Prepago, PrepagoAdmin)
site.register(Pago, PagoAdmin)
