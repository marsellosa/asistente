from django.forms import * #type: ignore
from comanda.models import Comanda, ComandaItem

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
    # fecha = DateField(initial=now, widget=DateInput(attrs=new_data))
    # class Meta:
    #     model = Comanda
    #     fields = ['fecha']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.fields:
    #         field_name = str(field)
    #         new_data = {
    #             'class' : 'form-control',
    #             '' : 'SelectDateWidget',
    #             'placeholder' : now
    #         }
    #         self.fields[field_name].widget.attrs.update(new_data)