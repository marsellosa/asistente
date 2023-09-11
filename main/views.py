import random
from datetime import date
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from productos.models import Categoria, Detalles
from bot.models import BotUser, Activity
from bot.forms import MessageForm
from comanda.models import Comanda
from main.models import Monto
from socios.models import Socio
from home.decorators import allowed_users

@staff_member_required
def bot_user_profile(request, user_id):
    context, template = {}, 'apps/bot/bot_user_profile.html'
    bot_user = BotUser.objects.get(user_id=user_id)
    form = MessageForm()
    if request.method == 'POST':
        form = MessageForm(request.POST or None)
    context = {
        'user': bot_user,
        'form': form
    }
    return render(request, template, context)

@staff_member_required
def detalle_ahorro(request):
    template = 'apps/main/detalle_ahorro.html'
    amounts_list = Monto.objects.all().order_by('-inserted_on')
    page = request.GET.get('page',  1)
    
    paginator = Paginator(amounts_list, 10)
    try:
        detalle = paginator.page(page)
    except PageNotAnInteger:
        detalle = paginator.page(1)
    except EmptyPage:
        detalle = paginator.page(paginator.num_pages)
    context = {
        'detalle' : detalle 
    }
    return render(request, template, context)


@staff_member_required
def users_list_view(request):
    template = 'apps/bot/users_list.html'
    context = {
        'users_list': BotUser.objects.all().order_by('-inserted_on')
    }

    return render(request, template, context)


@login_required
def inicio_view(request):
    context, template = {}, "apps/main/inicio.html"
    socios = Socio.objects.all()
    productos = Categoria.objects.all()
    detalles = Detalles.objects.all()
    users = BotUser.objects.all()
    # activities = Activity.objects.values('inserted_on__date').distinct().values('user_id').distinct()
    activities = Activity.objects.all().order_by('-inserted_on')[:25]
    comandas = Comanda.objects.filter(status='p')
    try:
        operador = request.user.groups.get(name='operadores')
    except:
        operador = None
    
    context = {
        'productos': productos,
        'detalles' : detalles,
        'users': users,
        'activities': activities,
        'comandas' : comandas,
        'operador' : operador,
        'socios' : socios,
        'latest' : socios.order_by('-persona__created_on__date')[:8],
    }

    return render(request, template, context)

def get_amount(ok):
    while ok:
        amount = random.randint(1,28)
        ok = False if Monto.objects.filter(monto=amount, inserted_on__icontains=date.today().year).count() <= 13 else True
            
    return amount

# SEARCH_TYPE_MAPPING = {
#     'receta': Receta,
#     'recetas': Receta,
#     'socio': Socio,
#     'socios': Socio
# }

# @staff_member_required
# def search_view(request):
#     context, template = {}, 'apps/main/search/results-view.html'
#     query = request.GET.get('q')
#     search_type = request.GET.get('type')
#     Klass = SEARCH_TYPE_MAPPING[search_type] if search_type in SEARCH_TYPE_MAPPING else Socio
#     qs = Klass.objects.search(query=query)
#     context['objects'] = qs

#     if request.htmx:
#         context['objects'] = qs[:5]
#         template = 'apps/main/search/partials/results.html'
    
#     return render(request, template, context)

@allowed_users(allowed_roles=['admin', 'operadores'])
def search_view(request):
    context, template = {}, 'apps/main/search/results-view.html'
    query = request.GET.get('q')
    qs = Socio.objects.search(query=query) #type: ignore
    context['objects'] = qs

    if request.htmx:
        context['objects'] = qs[:5]
        template = 'apps/main/search/partials/results.html'
    
    return render(request, template, context)

