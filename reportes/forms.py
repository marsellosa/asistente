from django.forms import * #type:ignore
from django.urls import reverse
from operadores.models import Operador
# from reportes.models import Ingreso

class ReporteDiarioForm(Form):

    def get_reporte_url(self):
        return reverse

    required_css_class = "required-field"
    new_data = {
                    'class' : 'form-control',
                    'type' : 'date',
                }

    fechadesde = DateField(help_text="Fecha de Inicio", widget=DateInput(attrs=new_data))
    # fechahasta = DateField(widget=DateInput(attrs={'class': 'form-control', 'type': 'date' }))
    
    class Meta:
        fields = ['fechadesde']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        codigo_operador = args[0]['codigo_operador'] if 'codigo_operador' in args[0] else None

        operador = Operador.objects.filter(codigo_operador=codigo_operador).first()
        
        url = operador.get_absolute_url() if operador else reverse('reportes:list')
        # url = reverse('reportes:by-operador', kwargs={'codigo_operador': codigo_operador}) if codigo_operador else reverse('reportes:list')
        self.fields['fechadesde'].widget.attrs.update(
            {
                'hx-get': url,
                'hx-trigger': 'change',
                'hx-target': '#consumo-results',
                'hx-select': '#consumo-results',
                'hx-swap': 'outerHTML'
            }
        )

# class IngresoForm(ModelForm):

#     model = Ingreso
    
#     class Meta:
#         fields = ['monto', 'tipo_ingreso', 'detalle', 'operador']