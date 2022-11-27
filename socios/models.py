from django.db.models import * #type: ignore
from persona.models import Persona
from operadores.models import Operador
from django.urls import reverse

class SocioQuerySet(QuerySet):
    def search(self, query=None):
        if query is None or query == "":
            return self.none()
        lookups = (
            Q(persona__nombre__icontains=query) |
            Q(persona__apellido__icontains=query)
        )
        print(f"Buscando en socios: {lookups}")
        return self.filter(lookups)

    def by_user_id(self, user_id):
        return self.filter(user_id=user_id)

    def by_usuario(self, usuario):
        return self.filter(usuario=usuario)

    def by_operador(self, operador):
        return self.filter(operador=operador)

    def by_operador_id(self, operador_id):
        return self.filter(operador_id=operador_id)
   

class SocioManager(Manager):
    def get_queryset(self):
        return SocioQuerySet(self.model, using=self._db)

    def by_operador_id(self, operador_id):
        return self.get_queryset().by_operador_id(operador_id)

    def search(self, query=None):
        return self.get_queryset().search(query=query)

class Socio(Model):
    persona = ForeignKey(Persona, on_delete=CASCADE)
    referidor = ForeignKey('Socio', on_delete=SET_NULL, blank=True, null=True)
    operador = ForeignKey(Operador, on_delete=SET_NULL, blank=True, null=True)
    timestamp = DateField(auto_now_add=True)

    objects = SocioManager()

    def get_absolute_url(self):
        return reverse("socios:profile", kwargs={"id": self.id})

    def get_hx_crud_url(self):
        return reverse("socios:hx-profile", kwargs={"id": self.id})
    
    # def get_datos_contacto(self):
    #     return self.contacto_set.all()
    
    def __str__(self):
        return str(self.persona)