from django.urls import path
from consumos.views import list_consumos_by_id_operador, create_delete_transferencia

app_name = 'consumos'

urlpatterns = [
    path('by_id_operador/<str:id_operador>/', list_consumos_by_id_operador, name='by-id-operador' ),
    path('hx/consumo/<str:id_consumo>/add_delete_transferencia/', create_delete_transferencia, name='crud_transferencia')
]
