from django.contrib.admin import * #type: ignore

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

class PrecioIngredienteInline(StackedInline):
    model = CostoIngrediente
    extra = 1


class RecetaAdmin(ModelAdmin):
    inlines = [RecetaIngredienteInline, RecetaIngredienteHerbalInline]
    list_display = ['nombre', 'get_costo_receta', 'get_total_receta', 'precio_publico']
    readonly_fields = ['timestamp', 'updated']
    raw_id_fields = ['usuario']

class RecetaIngredienteAdmin(ModelAdmin):
    # inlines = [PrecioIngredienteInline]
    list_display = ['ingrediente', 'receta', 'cantidad', 'unidad']

class RecetaIngredienteHerbalAdmin(ModelAdmin):
    list_display = ['categoria', 'get_total']

class CostoIngredienteAdmin(ModelAdmin):
    list_display = ['ingrediente', 'precio', 'cantidad_decimal', 'unidad']
    readonly_fields = ['cantidad_decimal']

site.register(Ingrediente)
site.register(Receta, RecetaAdmin)
site.register(RecetaIngrediente, RecetaIngredienteAdmin)
site.register(RecetaIngredienteHerbal, RecetaIngredienteHerbalAdmin)
site.register(CostoIngrediente, CostoIngredienteAdmin)


