from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
#
from comanda.forms import ComandaForm, ComandaItemForm, ComandaModelForm
from comanda.models import Comanda, ComandaStatus
from prepagos.models import Prepago
from prepagos.forms import PrepagoForm, PagoForm
from socios.models import Socio


User = settings.AUTH_USER_MODEL

@staff_member_required
def socios_list_view(request):
    context, template = {}, 'apps/socios/list.html'
    socios = Socio.objects.all()
    context = {'socios' : socios}

    return render(request, template, context)

@staff_member_required
def socio_profile_view(request, id=None):
    context, template = {}, 'apps/socios/profile.html'
    # obj = get_object_or_404(Socio, id=id)
    # print(f"pk: {id}")
    try:
        obj = Socio.objects.get(pk=id)
    except:
        obj = None
    if obj is None:
        # return HttpResponse("Not Found")
        return HttpResponseRedirect(reverse('main:error'))
        # template = 'apps/socios/profile.html'
    comanda, created = Comanda.objects.get_or_create(socio_id=id, usuario_id=request.user.id, status=ComandaStatus.PENDIENTE)
    
    prepagos = Prepago.objects.filter(activo=True, socio__id=id)
    context = {
        'socio_obj': obj,
        'parent_obj': comanda,
        'prepagos_obj': prepagos,
        'comanda_form': ComandaModelForm(obj),
        'form': ComandaItemForm(),
        'prepago_form': PrepagoForm(),
        'pago_form': PagoForm()
    }
    # print(f"Comanda: {context}")
    return render(request, template, context)

def hx_socio_crud(request, id=None):
    context, template = {}, 'apps/socios/profile.html'
    try:
        obj = ''
        # obj = Socio.objects.get(id=id)
    except:
        obj = None
    if obj is None:
        # if request.htmx:
        #     return HttpResponse("Not Found")
        template = 'apps/socios/profile.html'
    else:
        if request.method == 'PUT':
            print(f"request is PUT")
            # context['form'] = form
    context['object'] = obj
    return render(request, template, context)