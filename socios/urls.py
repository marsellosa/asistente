from django.urls import path
from socios.views import *

app_name = 'socios'

urlpatterns = [
    path('', socios_list_view, name='list'),
    path('profile/<int:id>', socio_profile_view, name='profile'),
    path('hx/profile/<int:id>', hx_socio_crud, name='hx-profile'),
]
