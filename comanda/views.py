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
    
@allowed_users(['admin', 'operadores'])
def hx_create_comanda_view(request, id_socio=None):
    context, template = {}, 'apps/comanda/partials/comanda-pendiente.html'
    
    if not request.htmx:
        raise Http404

    if request.method == 'POST':
        socio = Socio.objects.get(id=id_socio)
        # Verificar si el socio ya tiene una comanda pendiente
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
    # Validar si la solicitud es HTMX
    if not request.htmx:
        raise Http404("Solicitud no válida")

    # Obtener la comanda o lanzar un error 404 si no existe
    comanda = get_object_or_404(Comanda, id=id_comanda)

    # Inicializar contexto y plantilla por defecto
    context = {'parent_obj': comanda}
    template = 'apps/comanda/partials/table-form.html'
    form = ComandaItemForm(request.POST or None)

    # Manejo de solicitudes POST (Agregar/Actualizar cantidad)
    if request.method == 'POST':
        if form.is_valid():
            receta_id = request.POST.get('receta')
            cantidad = int(request.POST.get('cantidad', 0))

            # Crear o actualizar el item de la comanda
            obj, created = ComandaItem.objects.get_or_create(
                comanda=comanda,
                receta_id=receta_id,
                defaults={'cantidad': cantidad}
            )

            if not created:
                obj.cantidad += cantidad
                obj.save()

            # Reiniciar el formulario
            form = ComandaItemForm()

    # Manejo de solicitudes PUT (Editar item)
    elif request.method == 'PUT':
        comandaitem = get_object_or_404(ComandaItem, id=id_receta, comanda=comanda)
        form = ComandaItemForm(instance=comandaitem)
        template = 'apps/comanda/partials/edit-form.html'
        context['obj'] = comandaitem

    # Manejo de solicitudes PATCH (Actualizar item)
    elif request.method == 'PATCH':
        if form.is_valid():
            cantidad = int(form.cleaned_data['cantidad'])
            if cantidad > 0:
                ComandaItem.objects.update_or_create(
                    id=id_receta,
                    comanda=comanda,
                    defaults={
                        'receta': form.cleaned_data['receta'],
                        'cantidad': cantidad,
                    }
                )
            form = ComandaItemForm()

    # Manejo de solicitudes DELETE (Eliminar item)
    elif request.method == 'DELETE':
        comandaitem = get_object_or_404(ComandaItem, id=id_receta, comanda=comanda)
        comandaitem.delete()
        messages.success(request, "Receta eliminada correctamente")

    # Agregar el formulario al contexto
    context['comanda_item_form'] = form

    return render(request, template, context)

@allowed_users(['admin', 'operadores'])
def hx_add_prepago_view(request, id_comanda=None, id_prepago=None):
    """
    Vista para agregar o quitar un prepago de una comanda.
    """
    context = {}
    template = 'apps/comanda/partials/total.html'

    # Obtener la comanda y el prepago usando get_object_or_404
    comanda = get_object_or_404(Comanda, id=id_comanda, status='p')
    prepago = get_object_or_404(Prepago, id=id_prepago)

    # Verificar si el prepago ya está asociado a la comanda
    if prepago in comanda.prepago.all():
        comanda.prepago.remove(prepago)
    else:
        # Verificar si el saldo del prepago es suficiente
        if prepago.get_alert():
            messages.error(request, "No puede usar este prepago: alerta activa.")
        else:
            comanda.prepago.add(prepago)

    # Actualizar el estado del prepago
    prepago.activo = prepago.get_uses_list().count() < prepago.cantidad
    prepago.save()

    # Guardar la comanda y preparar el contexto
    comanda.save()
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

    template = 'apps/main/partials/status.html'

    # Obtiene la comanda o devuelve un error 404 si no existe
    comanda = get_object_or_404(Comanda, id=id_comanda)
    
    # Mapeo de estados: define cómo cambia el estado usando ComandaStatus
    status_map = {
        ComandaStatus.PENDIENTE: ComandaStatus.ENTREGADO,
        ComandaStatus.ENTREGADO: ComandaStatus.PENDIENTE,
    }
    
    # Verifica si el estado actual está en el mapeo
    if comanda.status in status_map:
        comanda.status = status_map[comanda.status]
        comanda.save()
    else:
        # Maneja el caso de un estado inesperado
        return render(request, template, {'message': 'Estado de comanda inválido.'})
    
    # Renderiza la plantilla con el contexto actualizado
    context = {'comanda': comanda}
    return render(request, template, context)

