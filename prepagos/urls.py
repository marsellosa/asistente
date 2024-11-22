from django.urls import path
from prepagos.views import *
app_name = 'prepagos'

urlpatterns = [
    path('<str:id>/',detail_view, name='detail'),
    path('list/operador/<int:id_operador>/', list_operador_view, name='list_operador'),
    path('create/<str:id_socio>/',create_prepago_view, name='create'),
    path('add/pago/<str:prepago_id>/',add_pago_view, name='add-pago'),
]
