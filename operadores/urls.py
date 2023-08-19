from django.urls import path
from operadores.views import *

app_name = 'operadores'

urlpatterns = [
    path('', list_view, name='list'),
    path('profile/<str:id>/', profile_view, name='profile'),
    path('hx/list_pedidos_by_operador/<str:id_operador>/', list_pedidos_by_operador, name='list-by-operador'),
    path('hx/list_socios_by_operador/<int:id>/', list_socios_by_operador, name='list-socios-by-operador'),
]
