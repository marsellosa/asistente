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
        raise Http404
    socio = Socio.objects.get(id=id_socio)
    prepagos = socio.prepago_set.filter(pagado=False)
    context = {
        'prepagos_obj': prepagos,
        'pago_form': PagoForm(),
        'socio_obj': socio,
    }
    
    if request.method == 'POST':
        template= 'apps/prepagos/partials/list-form.html'
        form = PrepagoForm(request.POST or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.socio = socio
            obj.save()
        
    if request.method == 'PUT':
        template = 'apps/prepagos/partials/prepago-form.html'
        context['prepago_form'] = PrepagoForm()
    
    return render(request, template, context)


@staff_member_required
def add_pago_view(request, prepago_id=None):
    context, template = {}, 'apps/prepagos/partials/prepago.html'
    if not request.htmx:
        raise Http404
    
    prepago = Prepago.objects.get(id=prepago_id) if prepago_id is not None else None    
    form = PagoForm(request.POST or None)
    
    if request.method == 'POST':
        # print(f"form: {form}")
        if form.is_valid():
            # print(f"form: {prepago}")
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
