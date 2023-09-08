from django.contrib.admin import * 
from socios.models import Socio
from prepagos.models import Prepago


class PrepagoInline(StackedInline):
    model = Prepago
    extra = 1
    autocomplete_fields = ['socio']

class SocioAdmin(ModelAdmin):
    inlines = [PrepagoInline]
    search_fields = ['persona__nombre', 'persona__apellido']

site.register(Socio,SocioAdmin)