from django.forms import * #type: ignore
from django.urls import reverse
from comanda.models import Comanda, ComandaItem
from prepagos.models import Prepago

class ComandaItemForm(ModelForm):

    required_css_class = "required-field"
    class Meta:
        model = ComandaItem
        fields = ['receta', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'class' : 'form-control',
            }
            self.fields[field_name].widget.attrs.update(new_data)


class ComandaForm(Form):

    new_data = {
        'class' : 'form-control',
        'type' : 'date',
    }
    
    fecha = DateField(widget=DateInput(attrs=new_data))

class ComandaModelForm(ModelForm):
    new_data = {
        'class' : 'form-control',
        'type' : 'date',
    }
    # prepago = MultipleChoiceField(choices=)
    fecha = DateField(widget=DateInput(attrs=new_data))
    class Meta:
        model = Comanda
        fields = ['fecha', 'prepago']

    def __init__(self, socio, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'class' : 'form-control',
                
            }
            self.fields[field_name].widget.attrs.update(new_data)
            # print(Prepago.get_prepagos_list)
        self.fields['prepago'].queryset = Prepago.objects.filter(socio=socio, activo=True)
        self.fields['prepago'].widget.attrs.update(
            {
                'hx-get': reverse('comanda:form'),
                'hx-trigger': 'select change click',
                'hx-target': '#total_a_pagar'
            }
        )