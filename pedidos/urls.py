from django.urls import path
from pedidos.views import *

app_name = 'pedidos'

urlpatterns = [
    path('', lista_pedidos, name='lista'),
    path('hx/', lista_pedidos, name='hx-lista'),
    path('crear/', crear_pedido, name='crear'),
    path('detail/<str:id_pedido>/', pedido_detail_view, name='detail'),
    path('hx/crear/<str:id_operador>/', crear_pedido_hx, name='hx-crear'),
    path('hx/delete/pedido/<int:pedido_id>/item/<int:id>/', hx_delete_item_view, name='hx-delete-item'),
    
    
]