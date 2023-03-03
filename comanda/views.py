from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib import messages
from comanda.forms import ComandaItemForm
from comanda.models import Comanda, ComandaItem, ComandaStatus
from prepagos.models import Prepago

from productos.models import *

User = settings.AUTH_USER_MODEL

def comanda_view(request):
    context, template = {}, 'apps/comanda/partials/total.html'
    prod = get_object_or_404(Categoria, nombre='BATIDO')
    url = Comanda.get_add_prepago_url
    print(f"url: {url}")
    query = dict(request.GET)['prepago']
    print(f"query: {query}")
    context = {'prod': prod}
    return render(request, template, context)
    # return HttpResponse(prod)

def hx_add_item_view(request, id_comanda=None, id_receta=None):
    # add/delete item for Comanda
    context, template = {}, 'apps/comanda/partials/table-form.html'
    msg = None
    if not request.htmx:
        return Http404

    comanda = Comanda.objects.get(id=id_comanda)
    form = ComandaItemForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            receta_id = request.POST.get('receta')
            # cant = request.POST.get('cantidad')
            # obj, created = ComandaItem.objects.update_or_create(
            #     comanda = comanda,
            #     receta__id = receta_id,
            #     defaults={'cantidad' : cant + obj.cantidad},
                
            # )

            try:
                receta_id = request.POST.get('receta')
                obj = ComandaItem.objects.get(comanda=comanda, receta__id=receta_id)
                if obj is not None:
                    cant = request.POST.get('cantidad')
                    obj.cantidad += int(cant) #type: ignore
                    obj.save()
            except:
                obj = form.save(commit=False)
                obj.comanda = comanda
                obj.save()
            form = ComandaItemForm()

    if request.method == 'PATCH':
        comandaitem = ComandaItem.objects.get(id=id_receta, comanda__id=id_comanda)
        args = {'receta': comandaitem.receta, 'cantidad': comandaitem.cantidad}
        form = ComandaItemForm(args)
        template = 'apps/comanda/partials/edit-form.html'

    if request.method == 'DELETE':
        obj = ComandaItem.objects.get(id=id_receta, comanda__id=id_comanda)
        obj.delete()
        messages.success(request, "Eliminado Correctamente")
        msg = 'Receta Eliminada'
        
    context = {
        'parent_obj': comanda,
        'form': form,
        'msg': msg
    }
    return render(request, template, context)

def hx_add_prepago_view(request, id_comanda=None):
    context, template = {}, 'apps/comanda/partials/total.html'
    valor = 0
    comanda = Comanda.objects.get(id=id_comanda, status='p')
    vendido = comanda.get_cart_total
    try:
        prepagos = dict(request.GET)['prepago']
    except:
        prepagos = []
    for id_prepago in prepagos:
        try:
            prepago = Prepago.objects.get(id=id_prepago, activo=True)
        except:
            prepago = None
        if prepago is not None:
            valor += prepago.valor
            vendido = vendido - valor
    context = {'pagar': vendido}

    print(f"prepagos, id_comanda, valor, vendido: {prepagos, id_comanda, valor, vendido}")
    return render(request, template, context)
