from django.http import Http404, HttpResponse
from django.shortcuts import render
from operadores.models import *
from pedidos.models import Pedido
from prepagos.models import Pago
from reportes.forms import ReporteDiarioForm
from reportes.utils import reporte_consumos
from socios.models import Socio
from home.decorators import allowed_users


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
        template = 'apps/reportes/reporte_card.html'
        
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

@allowed_users(['admin'])
def list_admin_view(request):
    context, template = {}, 'apps/operadores/list_admin.html'

    context = {
        'operadores' : Operador.objects.all(),
    }

    return render(request, template, context)

@allowed_users(['admin'])
def profile_admin_view(request, id_operador):
    context, template = {}, 'apps/operadores/profile-admin.html'

    context = reporte_consumos(id_operador=id_operador, user=request.user)
    context['form']= ReporteDiarioForm({'id': id_operador})

    return render(request, template, context)