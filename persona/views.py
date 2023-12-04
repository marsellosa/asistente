from django.shortcuts import render
from persona.models import Persona
from persona.forms import PersonaForm


# Create your views here.
def agregar_referido(request, id_referidor):
    context, template = {}, 'apps/personas/partials/agregar_referido.html'
    context = {
        'form': PersonaForm(),
        'id_referidor': id_referidor
        }
    return render(request, template, context)