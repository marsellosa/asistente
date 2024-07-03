from django.contrib.admin import * #type: ignore
from prepagos.models import Prepago, Pago,TransferenciaPP
# from socios.models import Socio

class TransferenciaPPInLine(StackedInline):
    model = TransferenciaPP

class PagoInline(StackedInline):
    model = Pago
    extra = 1

class PrepagoAdmin(ModelAdmin):
    inlines = [PagoInline]
    readonly_fields = ['descuento_decimal']
    list_display =  ['socio', 'valor', 'cantidad', 'descuento']

class PagoAdmin(ModelAdmin):
    inlines = [TransferenciaPPInLine]
    list_display = ['get_nombre_socio', 'monto', 'usuario', 'fecha']

class TransferenciaPPAdmin(ModelAdmin):
    list_display = ['socio','pago', 'usuario', 'inserted_on']


site.register(Prepago, PrepagoAdmin)
site.register(Pago, PagoAdmin)
site.register(TransferenciaPP, TransferenciaPPAdmin)
