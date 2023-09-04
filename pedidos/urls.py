from django.urls import path
from pedidos.views import *

app_name = 'pedidos'

urlpatterns = [
    path('', lista_pedidos, name='lista'),
    path('hx/', lista_pedidos, name='hx-lista'),
    path('crear/', crear_pedido, name='crear'),
    path('detail/<str:id_pedido>/', pedido_crud_view, name='detail'),
    path('hx/crear/<str:id_operador>/', pedido_crud_view, name='hx-crear'),
    path('hx/pedidoitem/pedido/<str:pedido_id>/add/', pedidoitem_crud_view, name='hx-add-item'),
    path('hx/pedidoitem/item/<str:item_id>/delete/', pedidoitem_crud_view, name='hx-delete-item'),
    path('hx/list_pedidos_by_operador/<str:id_operador>/', list_pedidos_by_operador, name='list-by-operador'),
    
    
]