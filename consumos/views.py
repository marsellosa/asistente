from django.shortcuts import render, get_object_or_404
from django.utils.timezone import datetime
from consumos.models import Consumo
from operadores.models import Operador
from reportes.forms import ReporteDiarioForm


def list_consumos_by_id_operador(request, id_operador):
    context, template = {}, 'apps/operadores/partials/consumos.html'
    operador = get_object_or_404(Operador, pk=id_operador)
    lista = Consumo.objects.by_id_operador(id_operador) #type:ignore
    date = request.GET.get('fechadesde')    
    if not date:
        date = datetime.today()

    consumos = lista.filter(inserted_on=date).order_by('-id')
    # print(f"consumos: {consumos}, id_operador: {id_operador}")
    context = {
        'operador': operador,
        'consumos': consumos,
        'form': ReporteDiarioForm({'id': id_operador})
    }
    return render(request, template, context)
