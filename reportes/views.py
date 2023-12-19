from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import Http404
from main.utils import get_today
from consumos.models import Consumo
from reportes.forms import ReporteDiarioForm
from home.decorators import allowed_users

@allowed_users(['admin', 'operadores'])
def reporte_diario(request, id_operador=None):
    context, template = {}, 'apps/reportes/list.html'
    
    date = request.GET.get('fechadesde')    
    if not date:
        date = get_today()
    
    lista = Consumo.objects.by_id_operador(id_operador) if type(id_operador) is int else Consumo.objects.all() #type: ignore
    consumos = lista.filter(comanda__fecha=date).order_by('pk')
    
    if request.htmx:
        if request.method == 'POST':
            fechaDesde = request.POST.get('fechadesde')
            fechaHasta = request.POST.get('fechahasta')
            try:
                consumos = lista.filter(comanda__fecha__gte=fechaDesde, comanda__fecha__lte=fechaHasta).order_by('pk')
            except ValidationError:
                messages.warning = (request, "faltan datos")
        template = 'apps/reportes/partials/results.html'

    context = {
        'consumos': consumos,
        'totales': {
            'sobre_rojo': round(sum([item.sobre_rojo for item in consumos]), 2),
            'mayoreo': round(sum([item.mayoreo for item in consumos]), 2),
            'insumos': round(sum([item.insumos for item in consumos]), 2),
            'insumos': round(sum([item.insumos for item in consumos]), 2),
            'descuento': round(sum([item.descuento for item in consumos]), 2),
            'sobre_verde': round(sum([item.sobre_verde for item in consumos]), 2),
            'efectivo': round(sum([item.efectivo for item in consumos]), 2),
            # 'efectivo_prepago': round(sum([item.monto for item in efectivo_prepago]), 2),
            # 'efectivo_consumos': round(sum([item.efectivo for item in registrados]), 2),
            # 'prepagos_x_id' : round(sum([item.monto for item in prepagos_operador]) ,2)

        },
        'form' : ReporteDiarioForm({'id': id_operador})
    }
    return render(request, template, context)

