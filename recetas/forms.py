from django.forms import * #type: ignore

from recetas.models import Receta, RecetaIngrediente, RecetaIngredienteHerbal

class RecipeForm(ModelForm):
    required_css_class = "required-field"
    nombre = CharField(help_text='Click aqui si necesitas <a href="/help">Ayuda</a>')
    class Meta:
        model = Receta
        fields = ['nombre', 'descripcion', 'instrucciones', 'precio_publico']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'placeholder': f"{field_name} de la Receta".capitalize(),
                'class' : 'form-control',
                # 'hx-post'   : '.',
                # 'hx-trigger': 'keyup changed delay:500ms',
                # 'hx-target' : '#recipe-container',
                # 'hx-swap'   : 'outerHTML'
            }
            self.fields[field_name].widget.attrs.update(new_data)

        self.fields['descripcion'].widget.attrs.update({'rows': '3'})
        self.fields['instrucciones'].widget.attrs.update({'rows': '4'})

class RecetaIngredienteForm(ModelForm):
    required_css_class = "required-field"
    class Meta:
        model = RecetaIngrediente
        fields = ['ingrediente', 'descripcion', 'cantidad', 'unidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'placeholder': f"{field_name} del Ingrediente".capitalize(),
                'class' : 'form-control'
            }
            self.fields[field_name].widget.attrs.update(new_data)
        self.fields['descripcion'].widget.attrs.update({'rows': '3'})

class RecetaIngredienteHerbalForm(ModelForm):
    required_css_class = "required-field"
    class Meta:
        model = RecetaIngredienteHerbal
        fields = ['categoria', 'descripcion', 'cantidad', 'unidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            field_name = str(field)
            new_data = {
                'placeholder': f"{field_name} del Ingrediente Herbal".capitalize(),
                'class' : 'form-control'
            }
            self.fields[field_name].widget.attrs.update(new_data)
        self.fields['descripcion'].widget.attrs.update({'rows': '3'})