from django.urls import path
from comanda.views import *

app_name = 'comanda'

urlpatterns = [
    path('', comanda_view, name='form'),
    path('hx/comanda/<int:id_comanda>/receta/add/', hx_add_item_view, name='hx-add-receta'),
    path('hx/comanda/<int:id_comanda>/receta/<int:id_receta>/delete/', hx_add_item_view, name='hx-delete-receta'),
]
