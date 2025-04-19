from django.http import Http404, HttpResponse
from django.shortcuts import render
from operadores.models import *
from reportes.forms import ReporteDiarioForm
from reportes.utils import reporte_consumos_diario, reporte_semanal
from socios.models import Socio
from home.decorators import allowed_users


@allowed_users(['admin', 'operadores'])
def list_view(request):
    context, template = {}, 'apps/operadores/list.html'
    try:
        operador = request.user.groups.get(name='operadores')
    except:
        operador = None

    context = {
        'obj_list' : Operador.objects.all(),
        'operador' : operador,
    }

    return render(request, template, context)

@allowed_users(['admin', 'operadores'])
def profile_view(request, codigo_operador):
    context, template = {}, 'apps/operadores/profile.html'
    # Obtener el nombre de la URL que hizo la solicitud
    url_name = request.resolver_match.url_name
    
    if url_name == 'profile_admin':
        template = 'apps/operadores/profile-admin.html'

    fechaDesde = request.GET.get('fechadesde')
        
    # context = reporte_consumos_diario(codigo_operador=codigo_operador, fechaDesde=fechaDesde, user=request.user)
    context = reporte_semanal(codigo_operador=codigo_operador, fecha=fechaDesde)
    context['form']= ReporteDiarioForm({'codigo_operador': codigo_operador})
    
    return render(request, template, context)


@allowed_users(['admin', 'operadores'])
def list_socios_by_operador(request, id=None):
    context, template = {}, 'apps/socios/socios.html'
    try:
        socios_x_operador = Socio.objects.by_operador_id(operador_id=id).order_by('-timestamp') #type: ignore
    except:
        socios_x_operador = None
    if socios_x_operador is None:
        if request.htmx:
            return HttpResponse("Not Found")
        raise Http404
    context['obj_list'] = socios_x_operador[:5]
    context['id_operador'] = id

    return render(request, template, context)

@allowed_users(['admin'])
def list_admin_view(request):
    context, template = {}, 'apps/operadores/list_admin.html'

    context = {
        'operadores' : Operador.objects.all(),
    }

    return render(request, template, context)

@allowed_users(['admin'])
def profile_admin_view(request, id_operador):
    context, template = {}, 'apps/operadores/profile-admin.html'

    context = reporte_consumos_diario(id_operador=id_operador, user=request.user)
    context['form']= ReporteDiarioForm({'id': id_operador})

    return render(request, template, context)