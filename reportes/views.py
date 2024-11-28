from django.shortcuts import render
from django.contrib.auth import get_user_model
from reportes.forms import ReporteDiarioForm
from reportes.utils import reporte_consumos, prepagos_list
from home.decorators import allowed_users
# rest_framework 

User = get_user_model()


@allowed_users(['admin', 'operadores'])
def reporte_diario(request, id_operador=None, fechaDesde=None, fechaHasta=None):
    context, template = {}, 'apps/reportes/list.html'
    
    fechaDesde = request.GET.get('fechadesde')    
   
    if request.htmx:
        if request.method == 'POST':
            fechaDesde = request.POST.get('fechadesde')
            fechaHasta = request.POST.get('fechahasta')

        template = 'apps/operadores/partials/consumos.html'
        # template = 'apps/reportes/partials/results.html'

    context = reporte_consumos(id_operador=id_operador, fechaDesde=fechaDesde, fechaHasta=fechaHasta, user=request.user)
    context['form'] = ReporteDiarioForm({'id': id_operador})

    return render(request, template, context)

@allowed_users(['admin', 'operadores'])
def reporte_prepagos(request, id_operador=None):
    context, template = {}, 'apps/prepagos/partials/lista_prepagos.html'
    context = {'prepagos': prepagos_list(id_operador)}
    # print(f"context: {context}")
    return render(request, template, context)