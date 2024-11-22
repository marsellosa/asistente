from django.http import Http404
from django.shortcuts import render, get_object_or_404
from prepagos.forms import PagoForm, PrepagoForm
from prepagos.models import Prepago, Pago, TransferenciaPP
from socios.models import Socio
from home.decorators import allowed_users

def detail_view(request, id=None):
    context, template = {}, 'apps/prepagos/detail.html'
    return render(request, template, context)

def list_view(request):
    context, template = {}, 'apps/prepagos/partials/list-form.html'
    return render(request, template, context)

@allowed_users(['admin', 'operadores'])
def list_operador_view(request, id_operador):
    context, template = {}, 'apps/prepagos/partials/lista_prepagos.html'
    return render(request, template, context)

@allowed_users(['admin', 'operadores'])
def create_prepago_view(request, id_socio=None):
    context, template = {}, 'apps/prepagos/partials/list-form.html'

    if not request.htmx:
        raise Http404
    # socio = Socio.objects.get(id=id_socio)
    socio = get_object_or_404(Socio, id=id_socio)
    prepagos = socio.prepago_set.filter(pagado=False) #type: ignore
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


@allowed_users(['admin', 'operadores'])
def add_pago_view(request, prepago_id):
    context, template = {}, 'apps/prepagos/partials/prepago.html'
    if not request.htmx:
        raise Http404
    
    prepago = get_object_or_404(Prepago, pk=prepago_id)
    
    form = PagoForm(request.POST or None)
    
    if request.method == 'POST':
        
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user
            obj.prepago = prepago
            obj.save()
            if form.cleaned_data['qr']:
                trans = TransferenciaPP.objects.create(pago=obj)
                
            form = PagoForm()

    context = {
        'prepago': prepago,
        'pago_form': form,
        'show': True
    }

    return render(request, template, context)
