from django.http import HttpResponse, Http404
from django.shortcuts import render
from pedidos.forms import *
from pedidos.models import *
# from productos.models import Detalles

def lista_pedidos(request):
    context, template = {}, 'apps/pedidos/list.html'
    obj_list = Pedido.objects.filter(usuario=request.user).order_by('-timestamp')
    if request.htmx:
        obj_list = obj_list[:5]
        template = 'apps/pedidos/partials/list.html'
    
    context['obj_list'] = obj_list

    return render(request, template, context)

def pedido_detail_view(request, id_pedido):
    context, template = {}, 'apps/pedidos/detail.html'
    parent_obj = Pedido.objects.get(id=id_pedido)
    items = parent_obj.get_all_items()
    try:
        bot_user_id = parent_obj.operador.licencia.persona.user_set.get().user_id
    except:
        bot_user_id = None

    allow = True if items and bot_user_id is not None else False

    form = PedidoItemModelForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                categoria_id = request.POST.get('categoria')
                sabor_id = request.POST.get('detalles')
                obj = PedidoItem.objects.get(pedido__id=id_pedido, categoria__id=categoria_id, detalles__id=sabor_id)
                if obj:
                    cant = request.POST.get('cantidad')
                    obj.cantidad += int(cant)
                    obj.save()
            except:
                obj = form.save(commit=False)
                obj.pedido = parent_obj
                obj.save()
            
            form = PedidoItemModelForm()
            template = 'apps/pedidos/partials/table-form.html'
    
    if request.method == 'PUT':
        # hx_update_status(parent_obj, PedidoStatus.ENTREGADO)
        parent_obj.status = PedidoStatus.ENTREGADO
        parent_obj.save()
        headers = {"HX-Redirect": parent_obj.get_absolute_url()}
        return HttpResponse("Updated", headers=headers)
    
    if request.method == 'DELETE':
        # hx_update_status(parent_obj, PedidoStatus.CANCELADO)
        parent_obj.status = PedidoStatus.CANCELADO
        parent_obj.save()
        headers = {"HX-Redirect": parent_obj.get_absolute_url()}
        return HttpResponse("Deleted", headers=headers)
    context = {
        'parent_obj': parent_obj,
        'allow': allow,
        'user_id': bot_user_id,
        'form': form
        }
    return render(request, template, context)


def hx_update_status(parent_obj, status):
    parent_obj.status = status
    parent_obj.save()
    headers = {"HX-Redirect": parent_obj.get_absolute_url()}
    return HttpResponse("OK", headers=headers)

def crear_pedido(request):
    context, template = {}, 'apps/pedidos/crear.html'
    form = PedidoForm(request.POST or None)
    context['form'] = form
    pedido_item_form = PedidoItemModelForm(request.POST or None)
    context['pedido_item_form'] = pedido_item_form
    
    if form.is_valid():
        print(f"form: {form}")
    if pedido_item_form.is_valid():
        print(f"pedido_item_form: {pedido_item_form}")
    return render(request, template, context)

def crear_pedido_hx(request, id_operador=None):
    context, template = {}, 'apps/pedidos/partials/list.html'
        
    if not request.htmx:
        raise Http404

    if request.method == 'POST' and id_operador is not None:
        operador = Operador.objects.get(id=id_operador)
        form = PedidoForm()
        parent_obj = form.save(commit=False)
        parent_obj.usuario = request.user
        parent_obj.operador = operador
        parent_obj.save()
        headers = {"HX-Redirect": parent_obj.get_absolute_url()}
        return HttpResponse("Created", headers=headers)
        
    obj_list = Pedido.objects.filter(operador=id_operador).order_by('-timestamp')[:5]
    context = {'obj_list': obj_list, 'id_operador': id_operador}
        
    return render(request, template, context)

def hx_delete_item_view(request, pedido_id=None, id=None):
    context, template = {}, 'apps/pedidos/partials/table-form.html'
    form = PedidoItemModelForm()
    parent_obj = Pedido.objects.get(id=pedido_id)
    context = {
        'parent_obj': parent_obj,
        'form': form
    }
    try:
        obj = PedidoItem.objects.get(pedido=parent_obj, id=id)
    except:
        obj = None
    if obj is None:
        if request.htmx:
            return HttpResponse("Not Found")
        raise Http404
    if request.method == "DELETE":
        context['msg'] = f"Se eliminó: {obj.cantidad} {obj.categoria} de {obj.detalles}"
        obj.delete()
            
    return render(request, template, context)
