from django.http import Http404, HttpResponse
from django.shortcuts import render
from operadores.models import *
from pedidos.models import Pedido
from socios.models import Socio

def list_view(request):
    context, template = {}, 'apps/operadores/list.html'
    context['obj_list'] = Operador.objects.all()

    return render(request, template, context)

def list_pedidos_by_operador(request, id=None):
    context, template = {}, 'apps/pedidos/partials/list.html'
    try:
        pedidos_x_operador = Pedido.objects.all().by_operador_id(operador_id=id).order_by('-timestamp')[:5] #type: ignore
    except:
        pedidos_x_operador = None
    if pedidos_x_operador is None:
        if request.htmx:
            return HttpResponse("Not Found")
        raise Http404
    context['obj_list'] = pedidos_x_operador
    context['id_operador'] = id

    return render(request, template, context)

def list_socios_by_operador(request, id=None):
    context, template = {}, 'apps/socios/socios.html'
    try:
        socios_x_operador = Socio.objects.by_operador_id(operador_id=id).order_by('-timestamp')
    except:
        socios_x_operador = None
    if socios_x_operador is None:
        if request.htmx:
            return HttpResponse("Not Found")
        raise Http404
    print(f"Cant de Socios: {socios_x_operador.count()}")
    context['obj_list'] = socios_x_operador[:5]
    context['id_operador'] = id

    return render(request, template, context)