from django.db.models import * #type:ignore
from django.urls import reverse
from persona.models import Licencia

class Operador(Model):
    licencia = OneToOneField(Licencia, verbose_name=("Operador Club"), on_delete=CASCADE)
    timestamp = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    @property
    def get_nivel_licencia(self):
        
        status = {
            'my': 'Mayorista',
            'pc': 'Productor Calificado',
            'cm': 'Consultor Mayor',
            'ds': 'Distribuidor'
        }

        return status[self.licencia.status]

    def get_absolute_url(self):
        return reverse("operadores:profile", kwargs={"id": self.pk})
    
    def get_profile_picture(self):
        return self.licencia.persona.get_profile_pic_url()

    def __str__(self):
        return str(self.licencia)