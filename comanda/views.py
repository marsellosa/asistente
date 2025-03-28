from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib import messages
from comanda.forms import ComandaItemForm
from comanda.models import Comanda, ComandaItem, ComandaStatus
from home.decorators import allowed_users
from prepagos.models import Prepago
from socios.models import Socio

from productos.models import *

User = settings.AUTH_USER_MODEL
@allowed_users(['admin', 'operadores'])
def comanda_view(request):
    context, template = {}, 'apps/comanda/partials/total.html'
    prod = get_object_or_404(Categoria, nombre='BATIDO')
    context = {'prod': prod}
    return render(request, template, context)
    # return HttpResponse(prod)
@allowed_users(['admin', 'operadores'])
def hx_create_comanda_view(request, id_socio=None):
    context, template = {}, 'apps/comanda/partials/comanda-pendiente.html'
    
    if not request.htmx:
        raise Http404

    if request.method == 'POST':
        socio = Socio.objects.get(id=id_socio)
        # parent_obj = Comanda.objects.create(usuario=request.user, socio=socio)
        parent_obj = Comanda.objects.get_or_create(
            socio=socio,
            status=ComandaStatus.PENDIENTE,  # Ajusta 'estado' según el campo de tu modelo
            defaults={'usuario': request.user}  # Solo se usa si se crea
        )[0]
        context = {
            'parent_obj': parent_obj,
            'comanda_item_form': ComandaItemForm()
            }
    
    return render(request, template, context)
@allowed_users(['admin', 'operadores'])
def hx_crud_comandaitem_view(request, id_comanda=None, id_receta=None):
    # add/delete item for Comanda
    context, template = {}, 'apps/comanda/partials/table-form.html'
    
    if not request.htmx:
        raise Http404

    comanda = Comanda.objects.get(id=id_comanda)
    form = ComandaItemForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            receta_id = request.POST.get('receta')
            obj, created = ComandaItem.objects.get_or_create(
                comanda=comanda, 
                receta__id=receta_id,
                defaults=form.cleaned_data
                )
            if not created:
                cant = request.POST.get('cantidad')
                obj.cantidad += int(cant) #type:ignore
                obj.save()

            form = ComandaItemForm()

    if request.method == 'PUT':
        comandaitem = ComandaItem.objects.get(id=id_receta, comanda__id=id_comanda)
        args = {'receta': comandaitem.receta, 'cantidad': comandaitem.cantidad}
        form = ComandaItemForm(args)
        template = 'apps/comanda/partials/edit-form.html'
        context['obj'] = comandaitem
    
    if request.method == 'PATCH':
        if form.is_valid():
            if int(form.cleaned_data['cantidad']) > 0:
                
                obj, created = ComandaItem.objects.update_or_create(
                    id=id_receta, comanda=comanda,
                    defaults={
                        'receta' : form.cleaned_data['receta'],
                        'cantidad' : form.cleaned_data['cantidad'],
                    }
                )
            form = ComandaItemForm()

    if request.method == 'DELETE':
        obj = ComandaItem.objects.get(id=id_receta, comanda__id=id_comanda)
        obj.delete()
        messages.success(request, "Receta Eliminada Correctamente")
    
    context['parent_obj'] = comanda
    context['comanda_item_form'] = form

    # context = {
    #     'parent_obj': comanda,
    #     'form': form,
    #     'msg': msg
    # }
    return render(request, template, context)
@allowed_users(['admin', 'operadores'])
def hx_add_prepago_view(request, id_comanda=None, id_prepago=None):
    context, template = {}, 'apps/comanda/partials/total.html'
    
    comanda = Comanda.objects.get(id=id_comanda, status='p')
    prepago = Prepago.objects.get(id=id_prepago)
    if prepago in comanda.prepago.all():
        comanda.prepago.remove(prepago)
    else:
        # TODO: verficar si su saldo alcanza
        comanda.prepago.add(prepago)
        if prepago.get_alert():
            comanda.prepago.remove(prepago)
            messages.error(request, "No puede usar este prepago")
    comanda.save()
    
    prepago.activo = True if prepago.get_uses_list().count() < prepago.cantidad else False
    prepago.save()
    context = {'parent_obj': comanda}
    return render(request, template, context)
@allowed_users(['admin', 'operadores'])
def comanda_item_edit_view(request, id_comanda_item):
    context, template = {}, 'apps/comanda/partials/comanda-item.html'
    if not request.htmx:
        raise Http404
    
    comanda_item = ComandaItem.objects.get(id=id_comanda_item)
    if request.method == 'POST':
        form = ComandaItemForm(request.POST or None)
        if form.is_valid():
            if int(form.cleaned_data['cantidad']) > 0:
                comanda_item.cantidad = int(form.cleaned_data['cantidad'])
                comanda_item.receta = form.cleaned_data['receta']
                comanda_item.save()
                template = 'apps/comanda/partials/table-form.html'
                context['parent_obj'] = comanda_item.comanda
                context['comanda_item_form'] = ComandaItemForm()
            
    context['obj']= comanda_item

    return render(request, template,context)
@allowed_users(['admin', 'operadores'])
def hx_update_status(request, id_comanda):
    context, template = {}, 'apps/pedidos/partials/item-deleted.html'
    comanda = get_object_or_404(Comanda, id=id_comanda)
    # comanda = Comanda.objects.get(id=id_comanda)
    if comanda.usuario == request.user:
        if comanda.comandaitem_set.all(): #type: ignore
            comanda.status = ComandaStatus.ENTREGADO
            comanda.save()
            messages.success(request, 'Comanda registrada')
            headers = {'HX-Redirect': comanda.socio.get_absolute_url()}
            return HttpResponse("Success", headers=headers)
        else:
            messages.error(request, 'La comanda esta vacia')
    else:
        messages.error(request, 'No es tu comanda')
    
    context = {'messages': [message for message in messages.get_messages(request)]}
        

    return render(request, template, context)

@allowed_users(['admin'])
def hx_admin_update_status(request, id_comanda):
    context, template = {}, 'apps/main/partials/status.html'
    comanda = get_object_or_404(Comanda, id=id_comanda)
    if comanda.status == 'p':
        status = 'e'
    elif comanda.status == 'e':
        status = 'p' 
    comanda.status = status
    comanda.save()
    context.update({'comanda': comanda})
    
    return render(request, template, context)