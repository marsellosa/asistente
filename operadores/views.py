from django.core.exceptions import ValidationError
from django.contrib import messages
from django_htmx.http import trigger_client_event
from django.http import Http404, HttpResponse
from django.shortcuts import render
from consumos.models import Consumo
from operadores.models import *
from pedidos.models import Pedido
from prepagos.models import Pago
from reportes.forms import ReporteDiarioForm
from reportes.utils import reporte_consumos
from socios.models import Socio
from home.decorators import allowed_users
from main.utils import get_today


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
        
    if request.htmx:
        template = 'apps/operadores/partials/consumos.html'
        
    context = reporte_consumos(id_operador=id, user=request.user)
    context['form']= ReporteDiarioForm({'id': id})
    
    return render(request, template, context)


@allowed_users(['admin', 'operadores'])
def list_socios_by_operador(request, id=None):
    context, template = {}, 'apps/socios/socios.html'
    try:
        socios_x_operador = Socio.objects.by_operador_id(operador_id=id).order_by('-timestamp') #type: ignore
    except:
        socios_x_operador = None
    if socios_x_operador is None:
        if request.htmx:
            return HttpResponse("Not Found")
        raise Http404
    context['obj_list'] = socios_x_operador[:5]
    context['id_operador'] = id

    return render(request, template, context)