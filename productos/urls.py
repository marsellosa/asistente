from django.urls import path
from productos.views import *
from productos.api import *

app_name = 'productos'

urlpatterns = [
    path('', app_over_view, name='api_products_overview'),
    path('api-list/', products_list, name='api_products_list'),
    path('api-create/', product_create, name='api_product_create'),
    path('api-search/', search_products, name='api_search_products'),
    path('api-detail/<str:pk>/', product_detail, name='api_products_detail'),
    path('api-update-or-create/<str:pk>/', product_update_or_create, name='api_product_update_or_create'),
    path('update/', update_db_view, name='update_bd'),
    path('hx/sabores/', hx_sabores_categoria, name='hx-sabores'),
]


