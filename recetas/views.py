from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse
from recetas.models import Receta, RecetaIngrediente, RecetaIngredienteHerbal
from recetas.forms import RecipeForm, RecetaIngredienteForm, RecetaIngredienteHerbalForm
# CRUD -> Create Read Update Delete

@login_required
def search_view(request):
    context, template = {}, 'apps/recetas/partials/search-results.html'
    query = request.GET.get('q')
    qs = Receta.objects.search(query=query)
    if not qs:
        qs = Receta.objects.all()
        print(f"No search results found")
    context['objects_list'] = qs

    return render(request, template, context)

@login_required
def recipe_list_view(request):
    context, template = {}, 'apps/recetas/list.html'
    qs = Receta.objects.filter(active=True)
    context['objects_list'] = qs
    return render(request, template, context)

@login_required
def recipe_detail_view(request, id=None):
    context, template = {}, 'apps/recetas/detail.html'
    obj = get_object_or_404(Receta, id=id, usuario=request.user)
    context['object'] = obj
    return render(request, template, context)

@login_required
def recipe_delete_view(request, id=None):
    context, template = {}, 'apps/recetas/delete.html'
    try:
        obj = Receta.objects.get(id=id, usuario=request.user)
    except:
        obj = None
    if obj is None:
        if request.htmx:
            return HttpResponse("Not Found")
        raise Http404
    if request.method == "POST":
        obj.delete()
        success_url = reverse('recetas:list')
        if request.htmx:
            headers = {'HX-Redirect': success_url}
            return HttpResponse("Success", headers=headers)
        return redirect(success_url)
    context['object'] = obj
    return render(request, template, context)

@login_required
def recipe_ingredient_delete_view(request, parent_id=None, id=None):
    context, template = {}, 'apps/recetas/delete.html'
    try:
        obj = RecetaIngrediente.objects.get(receta__id=parent_id, id=id, receta__usuario=request.user)
    except:
        obj = None
    if obj is None:
        if request.htmx:
            return HttpResponse("Not Found")
        raise Http404
    if request.method == "POST":
        obj.delete()
        success_url = reverse('recetas:detail', kwargs={'id': parent_id})
        if request.htmx:
            template = 'apps/recetas/partials/deleted.html'
        else:
            return redirect(success_url)
    context['object'] = obj
    return render(request, template, context)

@login_required
def recipe_herbal_ingredient_delete_view(request, parent_id=None, id=None):
    context, template = {}, 'apps/recetas/delete.html'
    try:
        obj = RecetaIngredienteHerbal.objects.get(receta__id=parent_id, id=id, receta__usuario=request.user)
    except:
        obj = None
    if obj is None:
        if request.htmx:
            return HttpResponse("Not Found")
        raise Http404
    if request.method == "POST":
        obj.delete()
        success_url = reverse('recetas:detail', kwargs={'id': parent_id})
        if request.htmx:
            template = 'apps/recetas/partials/deleted.html'
        else:
            return redirect(success_url)
    context['object'] = obj
    return render(request, template, context)

@login_required
def recipe_create_view(request):
    context, template = {}, 'apps/recetas/create-update.html'
    form = RecipeForm(request.POST or None)
    context['form'] = form
    if form.is_valid():
        obj = form.save(commit=False)
        obj.usuario = request.user
        obj.save()
        if request.htmx:
            headers = {"HX-Redirect": obj.get_absolute_url()}
            return HttpResponse("Created", headers=headers)
            # context['object'] = obj
            # template = 'apps/recetas/detail.html'
        return redirect(obj.get_absolute_url())
    return render(request, template, context)

@login_required
def recipe_update_view(request, id=None):
    template, context = 'apps/recetas/create-update.html', {}
    obj = get_object_or_404(Receta, id=id, usuario=request.user)
    form = RecipeForm(request.POST or None, instance=obj)
    new_ingredient_url = reverse('recetas:hx-ingredient-create', kwargs={'parent_id': obj.pk})
    new_herbal_ingredient_url = reverse('recetas:hx-herbal-ingredient-create', kwargs={'parent_id': obj.pk})
    context = {
        'new_herbal_ingredient_url': new_herbal_ingredient_url,
        'new_ingredient_url': new_ingredient_url,
        'object'    : obj,
        'form'      : form
    }
    if form.is_valid():
        form.save()
        context['message'] = 'Guardado'
    
    if request.htmx:
        template = 'apps/recetas/partials/forms.html'
    return render(request, template, context)

###################### HTMX ########################

@login_required #type:ignore
def recipe_detail_hx_view(request, id=None):
    context, template = {}, 'apps/recetas/partials/detail.html'
    if not request.htmx:
        return Http404
    try:
        obj = Receta.objects.get(id=id, usuario=request.user)
    except:
        obj = None
    if obj is None:
        return HttpResponse('Not Found')
    context['object'] = obj

    return render(request, template, context)

@login_required #type:ignore
def recipe_ingredient_update_hx_view(request, id=None, parent_id=None):
    context, template = {}, 'apps/recetas/partials/ingredient-form.html'
    if not request.htmx:
        return Http404
    try:
        parent_obj = Receta.objects.get(id=parent_id, usuario=request.user)
    except:
        parent_obj = None

    if parent_obj is None:
        return HttpResponse('Not Found')

    instance = RecetaIngrediente.objects.get(receta=parent_obj, id=id) if id is not None else None
    form = RecetaIngredienteForm(request.POST or None, instance=instance)
    url = instance.get_hx_edit_url() if instance else reverse('recetas:hx-ingredient-create', kwargs={'parent_id': parent_obj.id})
    context = {
        'url'   : url,
        'object': instance,
        'form'  : form
    }
    if form.is_valid():
        new_obj = form.save(commit=False)
        if instance is None:
            new_obj.receta = parent_obj
        new_obj.save()
        context['object'] = new_obj
        template = 'apps/recetas/partials/ingredient-inline.html'

    return render(request, template, context)

@login_required #type:ignore
def recipe_herbal_ingredient_update_hx_view(request, id=None, parent_id=None):
    context, template = {}, 'apps/recetas/partials/ingredient-form.html'
    if not request.htmx:
        return Http404
    try:
        parent_obj = Receta.objects.get(id=parent_id, usuario=request.user)
    except:
        parent_obj = None

    if parent_obj is None:
        return HttpResponse('Not Found')

    instance = RecetaIngredienteHerbal.objects.get(receta=parent_obj, id=id) if id is not None else None
    form = RecetaIngredienteHerbalForm(request.POST or None, instance=instance)
    url = instance.get_hx_edit_url() if instance else reverse('recetas:hx-herbal-ingredient-create', kwargs={'parent_id': parent_obj.id})
    context = {
        'url'   : url,
        'object': instance,
        'form'  : form
    }
    if form.is_valid():
        new_obj = form.save(commit=False)
        if instance is None:
            new_obj.receta = parent_obj
        new_obj.save()
        context['object'] = new_obj
        template = 'apps/recetas/partials/herbal-ingredient-inline.html'

    return render(request, template, context)

#############

@login_required
def htmx_crud_recipe_view(request, id=None):
    context, template = {}, 'apps/recetas/detail.html'
    receta = get_object_or_404(Receta, id=id, usuario=request.user)
    form = RecipeForm(request.POST or None, instance=receta)
    context['object'] = receta
    # Create
    if request.method == 'POST':
        template = 'apps/recetas/create-update.html'
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user
            obj.save()
            return redirect(obj.get_absolute_url())
            
    # Update
    if request.method == 'PUT':
        template = 'apps/recetas/create-update.html'
        context['form'] = form
        if form.is_valid():
            form.save()
            context['message'] = 'Data Saved'
    # Delete
    if request.method == 'DELETE':
        receta.delete()
        return HttpResponse('')
    
    return render(request, template, context)
