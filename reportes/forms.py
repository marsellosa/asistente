from django.forms import * #type:ignore
from django.urls import reverse
from operadores.models import Operador
from reportes.models import Ingreso

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
        url = reverse('reportes:by-operador', kwargs={'id_operador': id_operador}) if id_operador else reverse('reportes:list')
        self.fields['fechadesde'].widget.attrs.update(
            {
                'hx-get': url,
                'hx-trigger': 'change',
                'hx-target': '#consumo-results'
            }
        )

class IngresoForm(ModelForm):

    model = Ingreso
    
    class Meta:
        fields = ['monto', 'tipo_ingreso', 'detalle', 'operador']