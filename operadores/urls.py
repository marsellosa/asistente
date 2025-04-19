from django.urls import path
from operadores.views import *

app_name = 'operadores'

urlpatterns = [
    path('', list_view, name='list'),
    path('profile/<str:codigo_operador>/', profile_view, name='profile'),
    path('hx/list_socios_by_operador/<int:id>/', list_socios_by_operador, name='list-socios-by-operador'),
    # admin section
    path('admin/', list_admin_view, name='list_admin'),
    path('admin/profile/<str:id_operador>/', profile_view, name='profile_admin'),
]
