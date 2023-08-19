from django.shortcuts import render
from consumos.models import Consumo
from operadores.models import Operador
from reportes.forms import ReporteDiarioForm
from datetime import datetime

def list_consumos_by_id_operador(request, id_operador):
    context, template = {}, 'apps/operadores/partials/consumos.html'
    lista = Consumo.objects.by_id_operador(id_operador)
    date = request.GET.get('fechadesde')    
    if not date:
        date = datetime.today()

    consumos = lista.filter(inserted_on=date).order_by('-id')
    # print(f"consumos: {consumos}, id_operador: {id_operador}")
    context = {
        'operador': Operador.objects.get(id=id_operador),
        'consumos': consumos,
        'form': ReporteDiarioForm({'id': id_operador})
    }
    return render(request, template, context)
