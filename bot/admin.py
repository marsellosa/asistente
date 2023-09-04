from django.contrib import admin
from .models import BotUser, Activity
from .forms import BotUserForm

class BotUserAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'username']
    list_display = ['user_id', 'first_name', 'last_name', 'username', 'language_code', 'inserted_on']
    form = BotUserForm

class ActivityAdmin(admin.ModelAdmin):
    list_display = ['bot_user', 'text', 'inserted_on']

admin.site.register(BotUser, BotUserAdmin)
admin.site.register(Activity, ActivityAdmin)


# Register your models here.
