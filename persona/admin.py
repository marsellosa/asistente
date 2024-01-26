from django.contrib.admin import *
from persona.models import Persona, Licencia, Contacto
from socios.models import Socio

class SocioInline(StackedInline):
    model = Socio
    extra = 1
    search_fields = ['referidor']

class LicenciaInline(StackedInline):
    model = Licencia
    extra = 1

class PersonaAdmin(ModelAdmin):
    inlines = [SocioInline, LicenciaInline]

site.register(Persona, PersonaAdmin)
site.register(Licencia)
site.register(Contacto)
# Register your models here.
