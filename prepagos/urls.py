from django.urls import path
from prepagos.views import create_prepago_view, detail_view, add_pago_view

app_name = 'prepagos'

urlpatterns = [
    path('<int:id>/',detail_view, name='detail'),
    path('create/<int:id_socio>/',create_prepago_view, name='create'),
    path('add/pago/<int:prepago_id>/',add_pago_view, name='add-pago'),
]
