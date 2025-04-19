from django.shortcuts import render
from django.contrib.auth import get_user_model
from reportes.forms import ReporteDiarioForm
from reportes.utils import reporte_consumos_diario, prepagos_list, reporte_semanal
from home.decorators import allowed_users
from icecream import ic

User = get_user_model()

@allowed_users(['admin', 'operadores'])
def reporte_consumos(request, codigo_operador=None, fechaDesde=None, fechaHasta=None):
    context, template = {}, 'apps/reportes/list.html'
    
    fechaDesde = request.GET.get('fechadesde')

    url_name = request.resolver_match.url_name
    
    if url_name == 'reporte_semanal':
        context  = reporte_semanal(codigo_operador=codigo_operador, fecha=fechaDesde)
    elif url_name == 'by-operador' or url_name == 'list':
        context = reporte_consumos_diario(codigo_operador=codigo_operador, fechaDesde=fechaDesde, user=request.user)
   

    # context = reporte_consumos(codigo_operador=codigo_operador, fechaDesde=fechaDesde, fechaHasta=fechaHasta, user=request.user)
    # context = reporte_semanal(codigo_operador=codigo_operador, fecha=fechaDesde)
    context['form'] = ReporteDiarioForm({'codigo_operador': codigo_operador})

    # rep_semanal = reporte_semanal(fecha=fechaDesde, id_operador=id_operador)
    # print(rep_semanal)

    return render(request, template, context)



@allowed_users(['admin', 'operadores'])
def reporte_diario(request, id_operador=None, fechaDesde=None, fechaHasta=None):
    context, template = {}, 'apps/reportes/list.html'
    
    fechaDesde = request.GET.get('fechadesde')    
   
    if request.htmx:
        if request.method == 'POST':
            fechaDesde = request.POST.get('fechadesde')
            fechaHasta = request.POST.get('fechahasta')

    context = reporte_consumos(id_operador=id_operador, fechaDesde=fechaDesde, fechaHasta=fechaHasta, user=request.user)
    context['form'] = ReporteDiarioForm({'id': id_operador})

    # rep_semanal = reporte_semanal(fecha=fechaDesde, id_operador=id_operador)
    # print(rep_semanal)

    return render(request, template, context)

@allowed_users(['admin', 'operadores'])
def reporte_prepagos(request, id_operador=None):
    context, template = {}, 'apps/prepagos/partials/lista_prepagos.html'
    context = {'prepagos': prepagos_list(id_operador)}
    # print(f"context: {context}")
    return render(request, template, context)