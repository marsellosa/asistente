from django.urls import path
from comanda.views import *

app_name = 'comanda'

urlpatterns = [
    path('', comanda_view, name='form'),
    path('hx/comanda/<str:id_socio>/create/', hx_create_comanda_view, name='hx-create-comanda'), #type:ignore
    path('hx/comanda/<str:id_comanda>/prepago/<str:id_prepago>', hx_add_prepago_view, name='hx-add-prepago'), #type:ignore
    path('hx/<str:id_comanda>/status/update/', hx_update_status, name='hx-update-status'), #type:ignore
    path('hx/admin/<str:id_comanda>/status/update/', hx_admin_update_status, name='hx-admin-update-status'), #type:ignore
    path('hx/comanda/item/<int:id_comanda_item>/edit/', comanda_item_edit_view, name='hx-edit-item'), #type:ignore
    path('hx/comanda/<str:id_comanda>/receta/<str:id_receta>/delete/', hx_crud_comandaitem_view, name='hx-crud-comanda-item'), #type:ignore
]
