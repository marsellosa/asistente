from django.db.models import * #type:ignore
from django.urls import reverse
from persona.models import Licencia
import uuid


class Operador(Model):
    licencia = OneToOneField(Licencia, verbose_name=("Operador Club"), on_delete=CASCADE)
    codigo_operador = UUIDField(unique=True, default=uuid.uuid4, editable=False)
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
    
    def get_admin_url(self):
        return reverse('operadores:profile_admin', kwargs={'id_operador': self.id})

    def get_absolute_url(self):
        return reverse("operadores:profile", kwargs={"codigo_operador": self.codigo_operador})
    
    def get_profile_picture(self):
        return self.licencia.persona.get_profile_pic_url()
    
    class Meta:
        verbose_name = "Operador"
        verbose_name_plural = "Operadores"

    def __str__(self):
        return str(self.licencia)