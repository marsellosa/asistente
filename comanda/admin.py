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
    list_display = ['socio', 'usuario', 'fecha', 'get_cart_total', 'get_sobre_rojo']
    readonly_fields = ['timestamp', 'updated']
    raw_id_fields = ['usuario']
    # search_fields = ['socio']

site.register(Comanda, ComandaAdmin)
site.register(ComandaItem, ComandaItemAdmin)