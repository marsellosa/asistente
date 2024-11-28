from django.urls import path
from reportes.views import reporte_diario, reporte_prepagos

app_name = 'reportes'

urlpatterns = [
    path('', reporte_diario, name='list'),
    path('<int:id_operador>/', reporte_diario, name='by-operador'),
    path('hx/prepagos/operador/<int:id_operador>/', reporte_prepagos, name='pp-by-operador'),
]
