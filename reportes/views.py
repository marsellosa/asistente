from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import Http404
from datetime import datetime
from consumos.models import Consumo
from reportes.forms import ReporteDiarioForm
from home.decorators import allowed_users

@allowed_users(['admin', 'operadores'])
def reporte_diario(request, id_operador):
    context, template = {}, 'apps/reportes/list.html'
    
    date = request.GET.get('fechadesde')    
    if not date:
        date = datetime.today()
    lista = Consumo.objects.by_id_operador(id_operador)
    consumos = lista.filter(comanda__fecha=date).order_by('pk')
    # print(f"consumos: {consumos}")
    
    if request.htmx:
        if request.method == 'POST':
            fechaDesde = request.POST.get('fechadesde')
            fechaHasta = request.POST.get('fechahasta')
            try:
                consumos = lista.filter(comanda__fecha__gte=fechaDesde, comanda__fecha__lte=fechaHasta).order_by('pk')
            except ValidationError:
                messages.warning = (request, "faltan datos")
        template = 'apps/reportes/partials/results.html'
    print(f"sobre_rojo: {round(sum([item.sobre_rojo for item in consumos]), 2)}")
    print(f"mayoreo: {round(sum([item.mayoreo for item in consumos]), 2)}")    
    print(f"insumos: {round(sum([item.insumos for item in consumos]), 2)}")    
    print(f"puntos_volumen: {round(sum([item.puntos_volumen for item in consumos]), 2)}")    
    print(f"sobre_verde: {round(sum([item.sobre_verde for item in consumos]), 2)}")    
    print(f"total: {consumos.count()}")
    context = {
        'consumos': consumos,
        'totales': {
            'sobre_rojo': round(sum([item.sobre_rojo for item in consumos]), 2),
        },
        'form' : ReporteDiarioForm({'id': id_operador})
    }
    return render(request, template, context)