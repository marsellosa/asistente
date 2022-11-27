from django.http import Http404
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from prepagos.forms import PagoForm, PrepagoForm
from prepagos.models import Prepago, Pago
from socios.models import Socio

def detail_view(request, id=None):
    context, template = {}, 'apps/prepagos/partials/list-form.html'
    return render(request, template, context)

def list_view(request):
    context, template = {}, 'apps/prepagos/partials/list-form.html'
    return render(request, template, context)

@staff_member_required
def create_prepago_view(request, id_socio=None):
    context, template = {}, 'apps/prepagos/partials/list-form.html'
    if not request.htmx:
        return Http404
    socio = Socio.objects.get(id=id_socio)
    
    if request.method == 'POST':
        form = PrepagoForm(request.POST or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.socio = socio
            obj.save()
    form = PrepagoForm()
    pago_form = PagoForm()
    prepagos = Prepago.objects.filter(activo=True, socio=socio)
    context = {
        'prepagos_obj': prepagos,
        'prepago_form': form,
        'pago_form': pago_form,
        'socio_obj': socio,

    }

    return render(request, template, context)


@staff_member_required
def add_pago_view(request, prepago_id=None):
    context, template = {}, 'apps/prepagos/partials/prepago.html'
    if not request.htmx:
        return Http404

    prepago = Prepago.objects.get(id=prepago_id) if prepago_id is not None else None    
    form = PagoForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user
            obj.prepago = prepago
            obj.save()
            form = PagoForm()

    context = {
        'prepago': prepago,
        'pago_form': form,
        'show': True
    }

    return render(request, template, context)
