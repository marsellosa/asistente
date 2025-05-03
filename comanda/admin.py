from django.contrib.admin import *
from comanda.models import Comanda, ComandaItem

class ComandaItemInline(StackedInline):
    model = ComandaItem
    extra = 2

class ComandaItemAdmin(ModelAdmin):
    # search_fields = ['receta']
    list_display = ['receta', 'cantidad', 'get_total', 'get_costo']
    readonly_fields = ['timestamp', 'updated']

class ComandaAdmin(ModelAdmin):
    inlines = [ComandaItemInline]
    list_display = ['socio', 'usuario', 'fecha', 'cart_total']
    readonly_fields = ['timestamp', 'updated']
    raw_id_fields = ['usuario']
    
    # def sobre_rojo(self, obj):
    #     return obj.get_sobre_rojo
    # sobre_rojo.short_description = 'Sobre Rojo'

    def cart_total(self, obj):
        return obj.get_cart_total
    cart_total.short_description = 'Total'

site.register(Comanda, ComandaAdmin)
site.register(ComandaItem, ComandaItemAdmin)