from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from comanda.forms import ComandaItemForm
from comanda.models import Comanda, ComandaItem, ComandaStatus

from productos.models import *

User = settings.AUTH_USER_MODEL

def comanda_view(request):
    context, template = {}, 'apps/comanda/comanda.html'
    prod = get_object_or_404(Categoria, nombre='BATIDO')
    context = {'prod': prod}
    return render(request, template, context)

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
            try:
                receta_id = request.POST.get('receta')
                obj = ComandaItem.objects.get(comanda=comanda, receta__id=receta_id)
                if obj is not None:
                    cant = request.POST.get('cantidad')
                    obj.cantidad += int(cant)
                    obj.save()
            except:
                obj = form.save(commit=False)
                obj.comanda = comanda
                obj.save()
            form = ComandaItemForm()

    if request.method == 'DELETE':
        obj = ComandaItem.objects.get(id=id_receta, comanda__id=id_comanda)
        obj.delete()
        msg = 'Receta Eliminada'
        
    context = {
        'parent_obj': comanda,
        'form': form,
        'msg': msg
    }
    return render(request, template, context)


