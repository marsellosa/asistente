from django.urls import path
from operadores.views import *

app_name = 'operadores'

urlpatterns = [
    path('', list_view, name='list'),
    path('admin/', list_admin_view, name='list_admin'),
    path('profile/<str:id>/', profile_view, name='profile'),
    path('profile/admin/<str:id_operador>/', profile_admin_view, name='profile_admin'),
    path('hx/list_socios_by_operador/<int:id>/', list_socios_by_operador, name='list-socios-by-operador'),
]
