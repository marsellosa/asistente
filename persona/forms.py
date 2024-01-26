from django.forms import ModelForm, ModelChoiceField, CharField
from persona.models import Persona
from operadores.models import Operador

class PersonaForm(ModelForm):
    required_css_class = "required-field"

    operador = ModelChoiceField(Operador.objects.all())
    celular = CharField(max_length=8, required=False)
    
    class Meta:
        model = Persona
        fields = ['nombre', 'apellido', 'genero']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            
            field_name = str(field)
            
            new_data = {
                'placeholder': f"{field_name}".capitalize(),
                'class' : 'form-control',
            }
            self.fields[field_name].widget.attrs.update(new_data)
        