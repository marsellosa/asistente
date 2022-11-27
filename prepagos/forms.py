from django.forms import *
from prepagos.models import Prepago, Pago

class PrepagoForm(ModelForm):

    required_css_class = "required-field"
    class Meta:
        model = Prepago
        fields = ['valor', 'cantidad', 'descuento']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'class' : 'form-control',
            }
            self.fields[field_name].widget.attrs.update(new_data)

class PagoForm(ModelForm):

    required_css_class = "required-field"
    class Meta:
        model = Pago
        fields = ['fecha', 'monto']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'class' : 'form-control',
            }
            self.fields[field_name].widget.attrs.update(new_data)

