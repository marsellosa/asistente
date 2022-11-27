from django.contrib import admin
from .models import Settings, Monto


class SettingsAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'valor')

class MontoAdmin(admin.ModelAdmin):
    list_display = ('monto', 'inserted_on')

admin.site.register(Settings, SettingsAdmin)
admin.site.register(Monto, MontoAdmin)

# Register your models here.
