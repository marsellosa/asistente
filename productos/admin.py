from django.contrib.admin import *
from productos.models import *

class DetallesInline(StackedInline):
    model = Detalles
    extra = 1
    readonly_fields = ['cantidad_decimal']

class PrecioDistribuidorInline(StackedInline):
    model = PrecioDistribuidor
    extra = 1

class PrecioClientePreferenteInline(StackedInline):
    model = PrecioClientePreferente
    extra = 1

class CategoriaAdmin(ModelAdmin):
    inlines = [PrecioDistribuidorInline, PrecioClientePreferenteInline, DetallesInline]
    search_fields = ['nombre']
    list_display = ['nombre', 'activo']

class DetallesAdmin(ModelAdmin):
    list_display = ['sabor', 'categoria', 'descripcion']
    readonly_fields = ['cantidad_decimal']

class PorcionAdmin(ModelAdmin):
    list_display = ['categoria', 'precio', 'cantidad', 'unidad']
    readonly_fields = ['cantidad_decimal']

site.register(Categoria, CategoriaAdmin)
site.register(PrecioDistribuidor)
site.register(PrecioClientePreferente)
site.register(Pais)
site.register(Detalles, DetallesAdmin)
site.register(Porcion, PorcionAdmin)
site.register(PalabrasClave)
site.register(Sabor)
