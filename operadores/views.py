from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import render
from consumos.models import Consumo
from operadores.models import *
from pedidos.models import Pedido
from prepagos.models import Pago
from reportes.forms import ReporteDiarioForm
from socios.models import Socio
from home.decorators import allowed_users
from datetime import datetime


@allowed_users(['admin', 'operadores'])
def list_view(request):
    context, template = {}, 'apps/operadores/list.html'
    try:
        operador = request.user.groups.get(name='operadores')
    except:
        operador = None

    context = {
        'obj_list' : Operador.objects.all(),
        'operador' : operador,
    }

    return render(request, template, context)

@allowed_users(['admin', 'operadores'])
def profile_view(request, id=None):
    context, template = {}, 'apps/operadores/profile.html'
    date = request.GET.get('fechadesde')    
    if not date:
        date = datetime.today()
    lista = Consumo.objects.by_id_operador(id)
    consumos = lista.filter(comanda__fecha=date).order_by('-id')
    efectivo_prepago = Pago.objects.filter(fecha__date=date, usuario__id=id)
    print(f"Efectivo de prepagos: {Pago.objects.filter(fecha__date=date, usuario__id=id)}")
    if request.htmx:
        if request.method == 'POST':
            
            fechaDesde = request.POST.get('fechadesde')
            fechaHasta = request.POST.get('fechahasta')
            try:
                consumos = lista.filter(comanda__fecha__gte=fechaDesde, comanda__fecha__lte=fechaHasta).order_by('pk')
            except ValidationError:
                messages.warning = (request, "faltan datos")
            try:
                efectivo_prepago = Pago.objects.filter(fecha__date__gte=fechaDesde, fecha__date__lte=fechaHasta, usuario__id=id)
            except ValidationError:
                messages.warning = (request, "faltan datos en el formulario de fechas")
        template = 'apps/reportes/partials/results.html'
    context = {
        'operador': Operador.objects.get(id=id),
        'consumos': consumos,
        'totales': {
            'total': consumos.count(),
            'sobre_rojo': round(sum([item.sobre_rojo for item in consumos]), 2),
            'mayoreo': round(sum([item.mayoreo for item in consumos]), 2),
            'insumos': round(sum([item.insumos for item in consumos]), 2),
            'descuento': round(sum([item.descuento for item in consumos]), 2),
            'sobre_verde': round(sum([item.sobre_verde for item in consumos]), 2),
            'efectivo': round(sum([item.efectivo for item in consumos]), 2),
            'efectivo_prepago': round(sum([item.monto for item in efectivo_prepago]), 2),
        },
        'form': ReporteDiarioForm({'id': id})
    }
    return render(request, template, context)

@allowed_users(['admin', 'operadores'])
def list_pedidos_by_operador(request, id_operador=None):
    context, template = {}, 'apps/pedidos/partials/list.html'
    operador = Operador.objects.get(id=id_operador)
    pedidos = operador.pedido_set.all().order_by('-timestamp') #type: ignore
    if request.htmx:
        pedidos = pedidos[:5]
    context = {'obj_list': pedidos}

    return render(request, template, context)

@allowed_users(['admin', 'operadores'])
def list_socios_by_operador(request, id=None):
    context, template = {}, 'apps/socios/socios.html'
    try:
        socios_x_operador = Socio.objects.by_operador_id(operador_id=id).order_by('-timestamp')
    except:
        socios_x_operador = None
    if socios_x_operador is None:
        if request.htmx:
            return HttpResponse("Not Found")
        raise Http404
    context['obj_list'] = socios_x_operador[:5]
    context['id_operador'] = id

    return render(request, template, context)