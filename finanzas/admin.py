from django.contrib.admin import *
from finanzas.models import Movimiento

class MovimientoAdmin(ModelAdmin):
    list_display = ['__str__', 'semana', 'operador', 'monto']
    readonly_fields = ['created_at', 'updated_at']
    

site.register(Movimiento, MovimientoAdmin)

