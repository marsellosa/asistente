from django.db.models import * # type: ignore
from django.conf import settings
from django.urls import reverse
from main.models import Settings
from recetas.models import Receta
from socios.models import Socio
from prepagos.models import Prepago
from django.utils.timezone import now

User = settings.AUTH_USER_MODEL

class ComandaStatus(TextChoices):

    ENTREGADO = 'e', 'Entregado'
    CANCELADO = 'c', 'Cancelado'
    PENDIENTE = 'p', 'Pendiente'
    VENCIDO = 'v', 'Vencido'

class ComandaQuerySet(QuerySet):

    def by_user_id(self, user_id):
        return self.filter(user_id=user_id)

    def by_user(self, user):
        return self.filter(user=user)

    def candelado(self):
        return self.filter(status=ComandaStatus.CANCELADO)
        
    def entregado(self):
        return self.filter(status=ComandaStatus.ENTREGADO)

    def pendiente(self):
        return self.filter(status=ComandaStatus.PENDIENTE)

    def vencido(self):
        return self.filter(status=ComandaStatus.VENCIDO)

class ComandaManager(Manager):
    def get_queryset(self):
        return ComandaQuerySet(self.model, using=self._db)

class Comanda(Model):
    
    fecha = DateField(default=now)
    usuario = ForeignKey(User, on_delete=CASCADE)
    socio = ForeignKey(Socio, on_delete=CASCADE)
    prepago = ManyToManyField(Prepago, blank=True)
    timestamp = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    status = CharField(max_length=1, choices=ComandaStatus.choices, default=ComandaStatus.PENDIENTE)

    objects = ComandaManager()

    @property
    def get_add_receta_url(self):
        return reverse('comanda:hx-add-receta', kwargs={'id_comanda': self.pk})

    @property
    def get_total_comanda(self):
        comandaitems = self.comandaitem_set.all() # type: ignore
        total = sum([item.get_total for item in comandaitems])
        return total
    
    @property
    def get_sobre_rojo(self):
        comandaitems = self.comandaitem_set.all() # type: ignore
        sobre_rojo = sum([item.get_costo for item in comandaitems])
        try:
            porciento = float(Settings.objects.get(nombre='inversion').valor)
        except:
            porciento = 10
        re_inversion = self.porcentaje(sobre_rojo, porciento)
        return round(sobre_rojo + re_inversion, 1)

    @property
    def get_cart_total(self):
        comandaitems = self.comandaitem_set.all() # type: ignore
        total = sum([item.get_total for item in comandaitems])
        return total

    @property
    def get_mantenimiento(self):
        try:
            mant = float(Settings.objects.get(nombre='mantenimiento').valor)
        except:
            mant = 10
    
        return self.porcentaje(self.get_cart_total, mant)

    @property
    def get_cart_items(self):
        comandaitems = self.comandaitem_set.all() # type: ignore
        total = sum([item.cantidad for item in comandaitems])
        return total

    @property
    def get_cart_points(self):
        comandaitems = self.comandaitem_set.all() # type: ignore
        puntos = sum([item.get_puntos for item in comandaitems])
        return puntos

    def get_all_items(self):
        return self.comandaitem_set.all() # type: ignore

    def porcentaje(self, total, porciento):
        return total * porciento / 100


    def __str__(self):
        return str(self.socio)

class ComandaItem(Model):

    comanda = ForeignKey(Comanda, on_delete=CASCADE)
    receta = ForeignKey(Receta, on_delete=SET_NULL, null=True, blank=True)
    cantidad = IntegerField(default=1, blank=True, null=True)
    timestamp = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    @property
    def get_puntos(self):
        puntos = self.cantidad * self.receta.get_cart_points # type: ignore
        return puntos
    
    @property
    def get_total(self):
        total = self.cantidad * self.receta.precio_publico # type: ignore
        return total
    
    @property
    def get_costo(self):
        costo = self.cantidad * self.receta.get_costo_receta # type: ignore
        return costo

    def get_delete_url(self):
        return reverse('comanda:hx-delete-receta', kwargs={'id_receta': self.pk, 'id_comanda': self.comanda.pk})

    def __str__(self):
        return str(self.receta)