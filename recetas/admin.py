from django.contrib.admin import *

from .models import *

class RecetaIngredienteInline(StackedInline):
    model = RecetaIngrediente
    extra = 0
    readonly_fields = ['cantidad_decimal']
    # fields = ['nombre', 'cantidad', 'unidad', 'descripcion']

class RecetaIngredienteHerbalInline(StackedInline):
    model = RecetaIngredienteHerbal
    extra = 0
    readonly_fields = ['cantidad_decimal']
    # fields = ['categoria', 'cantidad', 'unidad', 'descripcion']


class RecetaAdmin(ModelAdmin):
    inlines = [RecetaIngredienteInline, RecetaIngredienteHerbalInline]
    list_display = ['nombre', 'get_costo_receta', 'get_total_receta', 'precio_publico']
    readonly_fields = ['timestamp', 'updated']
    raw_id_fields = ['usuario']

class RecetaIngredienteHerbalAdmin(ModelAdmin):
    list_display = ['categoria', 'get_total']

site.register(Receta, RecetaAdmin)
site.register(RecetaIngrediente)
site.register(RecetaIngredienteHerbal, RecetaIngredienteHerbalAdmin)


