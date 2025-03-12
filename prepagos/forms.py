from django.forms import * #type:ignore
from prepagos.models import Prepago, Pago

class PrepagoForm(ModelForm):

    required_css_class = "required-field"

    descuento = CharField(required=True, initial=10)

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
    qr = BooleanField(required=False)
    class Meta:
        model = Pago
        fields = ['qr', 'monto']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monto'].widget.attrs.update({'class' : 'form-control',})
