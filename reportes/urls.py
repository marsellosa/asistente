from django.urls import path
from reportes.views import reporte_diario

app_name = 'reportes'

urlpatterns = [
    path('', reporte_diario, name='list'),
    path('<int:id_operador>/', reporte_diario, name='by-operador'),
]
