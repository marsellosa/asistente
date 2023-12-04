from django.urls import path
from socios.views import *

app_name = 'socios'

urlpatterns = [
    path('', socios_list_view, name='list'),
    path('profile/<int:id>', socio_profile_view, name='profile'),
    path('hx/profile/<str:id_socio>', hx_socio_crud, name='hx-profile'),
    path('hx/asistencia/<str:id_socio>', hx_asistencia, name='hx-asistencia'),
    path('hx/referidos/<str:id_socio>', hx_referidos, name='hx-referidos'),
]
