from django.forms import * #type:ignore
from django.urls import reverse
from operadores.models import Operador

class ReporteDiarioForm(Form):

    def get_reporte_url(self):
        return reverse

    required_css_class = "required-field"
    new_data = {
                    'class' : 'form-control',
                    'type' : 'date',
                }

    fechadesde = DateField(help_text="Fecha de Inicio", widget=DateInput(attrs=new_data))
    fechahasta = DateField(widget=DateInput(attrs={'class': 'form-control', 'type': 'date' }))
    
    class Meta:
        fields = ['fechadesde', 'fechahasta']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        id_operador = args[0]['id']
        # print("ID: {}".format(id_operador))
        self.fields['fechadesde'].widget.attrs.update(
            {
                'hx-get': reverse('operadores:profile', kwargs={'id': id_operador}),
                'hx-trigger': 'change',
                'hx-target': '#consumo-results'
            }
        )

        