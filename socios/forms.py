from django.forms import *
from socios.models import *

class SocioForm(ModelForm):
    required_css_class = "required-field"
    class Meta:
        model = Socio
        fields = ['nombre', 'apellido', 'referidor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'placeholder': f"{field_name} del Socio".capitalize(),
                'class' : 'form-control',
            }
            self.fields[field_name].widget.attrs.update(new_data)
