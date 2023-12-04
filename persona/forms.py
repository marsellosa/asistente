from django.forms import ModelForm
from persona.models import Persona

class PersonaForm(ModelForm):
    required_css_class = "required-field"
    class Meta:
        model = Persona
        fields = ['nombre', 'apellido']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'placeholder': f"{field_name}".capitalize(),
                'class' : 'form-control',
            }
            self.fields[field_name].widget.attrs.update(new_data)