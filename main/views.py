import random
from datetime import date
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from productos.models import Categoria, Detalles
from bot.models import User, Activity
from bot.forms import MessageForm
from main.models import Monto
from recetas.models import Receta
from persona.models import Persona
from socios.models import Socio

@staff_member_required
def bot_user_profile(request, user_id):
    context, template = {}, 'apps/bot/bot_user_profile.html'
    bot_user = User.objects.get(user_id=user_id)
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
        'users_list': User.objects.all().order_by('-inserted_on')
    }

    return render(request, template, context)


@staff_member_required
def inicio_view(request):
    page_name = "apps/main/inicio.html"
    productos = Categoria.objects.all()
    detalles = Detalles.objects.all()
    users = User.objects.all()
    # activities = Activity.objects.values('inserted_on__date').distinct().values('user_id').distinct()
    activities = Activity.objects.all().order_by('-inserted_on')[:25]
    # print(activities)
    context = {
        'productos': productos,
        'detalles' : detalles,
        'users': users,
        'activities': activities
    }
 
    obj, created = Monto.objects.get_or_create(
        inserted_on = date.today(),
        defaults = {
            'monto' : get_amount(True)
        }
    )

    context['amount'] = obj.monto
    context['total'] = Monto.objects.aggregate(Sum('monto'))['monto__sum']

    return render(request, page_name, context)

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

@staff_member_required
def search_view(request):
    context, template = {}, 'apps/main/search/results-view.html'
    query = request.GET.get('q')
    qs = Socio.objects.search(query=query)
    context['objects'] = qs
    
    if request.htmx:
        context['objects'] = qs[:5]
        template = 'apps/main/search/partials/results.html'
    
    return render(request, template, context)