from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
#
from comanda.forms import ComandaItemForm, ComandaModelForm
from persona.forms import PersonaForm
from prepagos.forms import PrepagoForm, PagoForm
from comanda.models import Comanda, ComandaStatus
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
    context, template = context = {}, 'apps/socios/profile.html'

    obj = get_object_or_404(Socio, id=id)  # Obtener el socio o devolver 404
   
    # Intentar obtener la comanda pendiente
    comanda = Comanda.objects.filter(socio_id=id, status=ComandaStatus.PENDIENTE).first()
    
    # Obtener los prepago pendientes asociados al socio
    prepagos = obj.prepago_set.filter(pagado=False)  # type: ignore
    
    # Preparar datos del formulario ComandaModelForm
    comanda_data = {
        'comanda': comanda,
        'prepagos': prepagos
    }
    
    # Preparar el contexto para la plantilla
    context = {
        'socio_obj': obj,
        'parent_obj': comanda,
        'comanda_form': ComandaModelForm(comanda_data),
        'prepagos_obj': prepagos,
        'comanda_item_form': ComandaItemForm(),
        'prepago_form': PrepagoForm(),
        'pago_form': PagoForm(),
    }

    return render(request, template, context)

def hx_asistencia(request, id_socio):
    context, template = {}, 'apps/socios/partials/asistencia.html'
    socio = get_object_or_404(Socio, id=id_socio)
    context['comandas'] = socio.comanda_set.all().order_by('-fecha')[:5] #type:ignore

    return render(request, template, context)

def hx_referidos(request, id_socio):
    context, template = {}, 'apps/socios/partials/referidos.html'
    if not request.htmx:
        raise Http404
    
    socio = get_object_or_404(Socio, id=id_socio)
    referidos = socio.socio_set.all().order_by('-timestamp')[:50] #type:ignore
    context = {
        'referidos': referidos,
        'id_referidor': id_socio,
        'referidor': socio.referidor
        }
    
    return render(request, template, context)

def hx_socio_crud(request, id_socio=None):
    context, template = {}, 'apps/socios/profile.html'
    try:
        obj = ''
    except:
        obj = None

    return HttpResponse(obj)