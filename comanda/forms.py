from django.forms import * #type: ignore
from django.urls import reverse
from comanda.models import Comanda, ComandaItem
from prepagos.models import Prepago
from recetas.models import Receta

class ComandaItemForm(ModelForm):

    receta = ModelChoiceField(Receta.objects.all().order_by('nombre'))

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
    
    fecha = DateField(widget=DateInput(attrs=new_data))
    class Meta:
        model = Comanda
        fields = ['fecha', 'prepago']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        comanda_ = args[0]['comanda']
        prepagos_ = args[0]['prepagos']
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'class' : 'form-control',
                
            }
            self.fields[field_name].widget.attrs.update(new_data)
            # print(Prepago.get_prepagos_list)
        self.fields['prepago'].queryset = prepagos_
        self.fields['prepago'].widget.attrs.update(
            {
                'hx-get': '',
                'hx-trigger': 'change',
                'hx-target': '#total_a_pagar'
            }
        )