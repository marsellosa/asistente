from django.urls import path
from prepagos.views import create_prepago_view, detail_view, add_pago_view

app_name = 'prepagos'

urlpatterns = [
    path('<str:id>/',detail_view, name='detail'),
    path('create/<str:id_socio>/',create_prepago_view, name='create'),
    path('add/pago/<str:prepago_id>/',add_pago_view, name='add-pago'),
]
