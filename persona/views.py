from django.shortcuts import render, get_object_or_404
from persona.models import Persona
from socios.models import Socio
from persona.forms import PersonaForm


# Create your views here.
def agregar_referido(request, id_referidor):
    context, template = {}, 'apps/personas/partials/agregar_referido.html'
    context = {
        'form': PersonaForm(),
        'id_referidor': id_referidor
        }
    if request.method == 'POST':
        form = PersonaForm(request.POST or None)
        if form.is_valid():
            referidor = get_object_or_404(Socio, id=id_referidor)
            persona = Persona.objects.create(
                usuario = request.user,
                nombre=form.cleaned_data['nombre'],
                apellido=form.cleaned_data['apellido'],
                genero=form.cleaned_data['genero']
            )
            socio = Socio.objects.create(
                persona=persona,
                referidor=referidor,
                operador=form.cleaned_data['operador']
            )
            referidos = referidor.socio_set.all().order_by('-timestamp')[:50] #type:ignore
            context['referidos'] = referidos
            context['referidor'] = referidor.referidor
            template = 'apps/socios/partials/referidos.html'
    
    return render(request, template, context)