from django.conf import settings
from django.utils.timezone import now
from main.utils import get_today
from django.db.models import * #type:ignore
from socios.models import Socio
from django.urls import reverse

User = settings.AUTH_USER_MODEL

class PrepagoQuerySet(QuerySet):
    
    def by_socio(self, socio):
        return self.filter(socio=socio)

class PrepagoManager(Manager):
    def get_queryset(self):
        return PrepagoQuerySet(self.model, using=self._db)

    def by_socio(self, socio):
        return self.get_queryset().by_socio(socio)

class Prepago(Model):
    socio       = ForeignKey(Socio, on_delete=CASCADE)
    cantidad    = IntegerField(default=10)
    descuento   = FloatField(default=10)
    valor       = FloatField()
    pagado      = BooleanField(default=False)
    activo      = BooleanField(default=True)
    created     = DateTimeField(auto_now_add=True)
    edited      = DateTimeField(auto_now=True)
    descuento_decimal = FloatField()

    objects     = PrepagoManager()

    def get_absolute_url(self):
        return reverse("prepagos:detail", kwargs={ "id": self.pk })

    def get_total_pagos(self):
        return self.pago_set.all().order_by('-fecha') #type:ignore
    
    def get_uses_list(self):
        return self.comanda_set.all().order_by('-fecha') #type:ignore

    def get_acumulado(self):
        return round(sum([pago.monto for pago in self.get_total_pagos()]), 1)
    
    def get_saldo(self):
        total = self.valor * self.cantidad
        descuento = total * self.descuento / 100
        return round(total - descuento - self.get_acumulado(), 2)

    def __str__(self):
        return str(self.valor)

    def save(self, *args, **kwargs):
        self.descuento_decimal = self.valor * self.descuento / 100
        super().save(*args, **kwargs)

class PagoQuerySet(QuerySet):
    def pago_by_user(self, user):
        return self.filter(usuario=user)
    
    def pago_by_id(self, id):
        return self.filter(id=id)

class PagoManager(Manager):
    def get_queryset(self):
        return PagoQuerySet(self.model, using=self._db)
    
    def pago_by_user(self, user):
        return self.get_queryset().pago_by_user(user)
    
    def pago_by_id(self, id):
        return self.get_queryset().pago_by_id(id)

class Pago(Model):
    prepago = ForeignKey(Prepago, on_delete=CASCADE)
    monto = FloatField()
    fecha = DateTimeField(default=get_today)
    usuario = ForeignKey(User, on_delete=CASCADE)
    timestamp = DateTimeField(auto_now_add=True)

    def get_nombre_socio(self):
        return str(self.prepago.socio)
    
    def __str__(self):
        return str(self.monto)
