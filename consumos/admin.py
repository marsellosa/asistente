from django.contrib.admin import * #type:ignore
from consumos.models import Consumo, Transferencia

class ConsumoAdmin(ModelAdmin):
    # search_fields = ['receta']
    list_display = ['comanda', 'total_consumido', 'sobre_rojo', 'mayoreo', 'insumos', 'descuento', 'sobre_verde', 'puntos_volumen']
    readonly_fields = ['inserted_on', 'edited_on']

class TransferenciaAdmin(ModelAdmin):
    list_display = ['consumo', 'get_monto', 'inserted_on']

site.register(Consumo, ConsumoAdmin)
site.register(Transferencia, TransferenciaAdmin)