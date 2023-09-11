from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render
#
from comanda.forms import ComandaItemForm, ComandaModelForm
from comanda.models import Comanda, ComandaStatus
from prepagos.models import Prepago
from prepagos.forms import PrepagoForm, PagoForm
from socios.models import Socio
from home.decorators import allowed_users


User = settings.AUTH_USER_MODEL

@allowed_users(allowed_roles=['admin', 'operadores'])
def socios_list_view(request):
    context, template = {}, 'apps/socios/list.html'
    socios = Socio.objects.all()
    context = {'socios' : socios}

    return render(request, template, context)

@allowed_users(allowed_roles=['admin', 'operadores'])
def socio_profile_view(request, id=None):
    context, template = {}, 'apps/socios/profile.html'
    lista = ''
    try:
        obj = Socio.objects.get(pk=id)
    except:
        obj = None
    if obj is None:
        return HttpResponse("Profile not Found")
        
    try:
        comanda = Comanda.objects.get(socio_id=id, status=ComandaStatus.PENDIENTE)
        lista = comanda.prepago.all()
    except:
        comanda = None
    
    prepagos = obj.prepago_set.filter(pagado=False) #type:ignore

    context = {
        'socio_obj': obj,
        'parent_obj': comanda,
        'comanda_form': ComandaModelForm({'comanda': comanda, 'prepagos': prepagos}),
        'prepagos_obj': prepagos,
        'comanda_item_form': ComandaItemForm(),
        'prepago_form': PrepagoForm(),
        'pago_form': PagoForm()
    }
    return render(request, template, context)

def hx_asistencia(request, id_socio):
    context, template = {}, 'apps/socios/partials/asistencia.html'
    socio = Socio.objects.get(id=id_socio)
    context['comandas'] = socio.comanda_set.all().order_by('-fecha')[:5] #type:ignore

    return render(request, template, context)

def hx_socio_crud(request, id_socio=None):
    context, template = {}, 'apps/socios/profile.html'
    try:
        obj = ''
    except:
        obj = None

    return HttpResponse(obj)