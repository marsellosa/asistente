from django.urls import path
from consumos.views import list_consumos_by_id_operador

app_name = 'consumos'

urlpatterns = [
    path('by_id_operador/<str:id_operador>/', list_consumos_by_id_operador, name='by-id-operador' ),
]
