from django.shortcuts import render, get_object_or_404
from consumos.models import Consumo, Transferencia
from main.utils import get_today
from operadores.models import Operador
from reportes.forms import ReporteDiarioForm


def list_consumos_by_id_operador(request, id_operador):
    context, template = {}, 'apps/operadores/partials/consumos.html'
    operador = get_object_or_404(Operador, pk=id_operador)
    lista = Consumo.objects.by_id_operador(id_operador) #type:ignore
    date = request.GET.get('fechadesde')    
    if not date:
        date = get_today()

    consumos = lista.filter(inserted_on=date).order_by('-id')
    
    context = {
        'operador': operador,
        'consumos': consumos,
        'form': ReporteDiarioForm({'id': id_operador})
    }
    return render(request, template, context)

def create_delete_transferencia(request, id_consumo):
    context, template = {}, 'apps/comanda/partials/transfer.html'
    consumo = get_object_or_404(Consumo, pk=id_consumo)
    
    obj, created = Transferencia.objects.get_or_create(consumo=consumo)
    if not created:
        obj.delete()
        template = 'apps/comanda/partials/dollar.html'

    return render(request, template, context)