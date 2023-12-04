from django.urls import path
from persona.views import agregar_referido

app_name = 'personas'

urlpatterns = [
    # path('', reporte_diario, name='list'),
    path('agregar-referido/<str:id_referidor>/', agregar_referido, name='agregar-referido'),
]