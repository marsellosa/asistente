from django.contrib import admin
from .models import User, Activity
from .forms import UserForm

class UserAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'username']
    list_display = ['user_id', 'first_name', 'last_name', 'username', 'language_code', 'inserted_on']
    form = UserForm

class ActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'inserted_on']

admin.site.register(User, UserAdmin)
admin.site.register(Activity, ActivityAdmin)


# Register your models here.
