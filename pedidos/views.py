from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from home.decorators import allowed_users
from icecream import ic
from pedidos.forms import *
from pedidos.models import *
ic.disable()
def lista_pedidos(request):
    context, template = {}, 'apps/pedidos/list.html'
    obj_list = Pedido.objects.all().order_by('-timestamp')
    if request.htmx:
        obj_list = obj_list[:5]
        template = 'apps/pedidos/partials/list.html'
    
    context['obj_list'] = obj_list

    return render(request, template, context)

def crear_pedido_hx(request, id_operador=None):
    context, template = {}, 'apps/pedidos/partials/list.html'
    
    if request.method == 'POST':
        operador = get_object_or_404(Operador, id=id_operador)
        pedido = Pedido.objects.create(
            usuario = request.user,
            operador = operador
        )
        if request.htmx:
            headers = {"HX-Redirect": pedido.get_absolute_url()}
            return HttpResponse("Created", headers=headers)
        
    obj_list = Pedido.objects.filter(operador=id_operador).order_by('-timestamp')[:5]
    context = {'obj_list': obj_list, 'id_operador': id_operador}
        
    return render(request, template, context)

def pedido_crud_view(request, id_pedido=None, id_operador=None):
    context, template = {}, 'apps/pedidos/detail.html'
    pedido = get_object_or_404(Pedido, pedido_id=id_pedido)

    context['parent_obj'] = pedido
        
    if request.method == 'POST' and id_operador: 
        pedido = Pedido.objects.create(
            usuario = request.user,
            operador = Operador.objects.get(id=id_operador)
        )
        headers = {"HX-Redirect": pedido.get_absolute_url()}
        return HttpResponse("Created", headers=headers)

    if request.method == 'PUT':
        # pedido = Pedido.objects.get(pedido_id=id_pedido)
        pedido.status = PedidoStatus.ENTREGADO
        pedido.save()
        headers = {"HX-Redirect": pedido.get_absolute_url()}
        return HttpResponse("Updated", headers=headers)
    
    if request.method == 'DELETE':
        # pedido = Pedido.objects.get(pedido_id=id_pedido)
        pedido.status = PedidoStatus.CANCELADO
        pedido.save()
        headers = {"HX-Redirect": pedido.get_absolute_url()}
        return HttpResponse("Updated", headers=headers)

    context['form'] = PedidoItemModelForm

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



def pedidoitem_crud_view(request, pedido_id=None, item_id=None):
    context, template = {}, 'apps/pedidos/partials/table-form.html'
    try:
        pedido = Pedido.objects.get(pedido_id=pedido_id)
    except Pedido.DoesNotExist:
        pedido = PedidoItem.objects.get(id=item_id).pedido

    if request.method == 'POST':
        form = PedidoItemModelForm(request.POST or None)
        if form.is_valid():
            categoria_id = request.POST.get('categoria')
            detalles_id = request.POST.get('detalles')
            obj, created = PedidoItem.objects.get_or_create(
                pedido = Pedido.objects.get(pedido_id=pedido_id),
                categoria = Categoria.objects.get(id=categoria_id),
                detalles = Detalles.objects.get(id=detalles_id),
                defaults={
                    'cantidad': request.POST.get('cantidad'),
            })
            if not created:
                obj.cantidad += int(request.POST.get('cantidad'))
                obj.save()
        
    
            # context = {
            #     'parent_obj': obj.pedido,
            #     'form': PedidoItemModelForm
            # }

    if request.method == "DELETE":
        try:
            obj = PedidoItem.objects.get(id=item_id)
        except:
            obj = None
        if obj is None:
            if request.htmx:
                return HttpResponse("Not Found")
            raise Http404
        
        context['msg'] = f"Se eliminó: {obj.cantidad} {obj.categoria} de {obj.detalles}"
        obj.delete()

    # allow = True if pedido.get_all_items() and bot_user_id else False
    context = {
                'parent_obj': pedido,
                # 'allow': allow,
                # 'user_id': bot_user_id,
                'form': PedidoItemModelForm
            }
    
            
    return render(request, template, context)

class PedidoStatus:
    PENDIENTE = 'p'
    ENTREGADO = 'e'

@allowed_users(['admin', 'operadores'])
def list_pedidos_by_operador(request, id_operador=None):
    context, template = {}, 'apps/pedidos/list.html'
    operador = get_object_or_404(Operador, pk=id_operador)
    
    # Filter and order pedidos
    pedidos = operador.pedido_set.filter(
        status__in=[PedidoStatus.PENDIENTE, PedidoStatus.ENTREGADO]
    ).order_by('-timestamp')
    
    # Handle HTMX requests
    if request.htmx:
        pedidos = pedidos[:5]
        ic(pedidos)
        template = 'apps/pedidos/partials/list.html'

    # Safely retrieve bot_user_id
    bot_user_id = (
        operador.licencia.persona.get_bot_id
        if operador.licencia and operador.licencia.persona
        else None
    )
    ic(bot_user_id)
    # Build context
    context = {
        'obj_list': pedidos,
        'operador': operador,
        'bot_user_id': bot_user_id,
    }
    ic(context)
    return render(request, template, context)

