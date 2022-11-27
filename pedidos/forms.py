from django import forms
from django.urls import reverse
from pedidos.models import *

class PedidoForm(forms.ModelForm):
    
    class Meta:
        model = Pedido
        fields = ['operador']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'class' : 'form-control',
            }
            self.fields[field_name].widget.attrs.update(new_data)


class PedidoItemModelForm(forms.ModelForm):
    required_css_class = "required-field"
    class Meta:
        model = PedidoItem
        fields = ['categoria', 'detalles', 'cantidad']

    def get_flavor_url(self):
        return reverse('productos:hx-sabores')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'class' : 'form-control',
            }
            self.fields[field_name].widget.attrs.update(new_data)

        self.fields['categoria'].widget.attrs.update(
            {
                'hx-get': self.get_flavor_url(),
                'hx-trigger': 'change',
                'hx-target': '#id_detalles',
            
            }
            )

class PedidoItemForm(forms.Form):

    f = {}

    categoria = forms.CharField(label='Categoria', max_length=10, required=False)  #CharField(label='Categoria', max_length=100)
    detalles = forms.ComboField(fields=f)
    cantidad = forms.CharField(label='Cantidad', max_length=3)

    class Meta:
        fields = ['categoria', 'detalles', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'class' : 'form-control',
            }
            self.fields[field_name].widget.attrs.update(new_data)

        self.fields['categoria'].widget.attrs.update(
            {
                'hx-get': "sabores/",
                'hx-trigger': 'change',
                'hx-target': '#id_detalles',
            
            }
            )
