from django.urls import path
from reportes.views import reporte_diario, reporte_prepagos, reporte_consumos

app_name = 'reportes'

urlpatterns = [
    path('', reporte_consumos, name='list'),
    path('<str:codigo_operador>/', reporte_consumos, name='by-operador'),
    path('hx/prepagos/operador/<int:id_operador>/', reporte_prepagos, name='pp-by-operador'),
]
