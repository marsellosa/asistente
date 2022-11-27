from django.contrib.admin import * 
from socios.models import Socio

class SocioAdmin(ModelAdmin):
    search_fields = ['persona']

site.register(Socio,SocioAdmin)