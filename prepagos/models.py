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
    
    def total_gastado(self):
        return self.get_uses_list().count() * self.valor
        # return int(self.get_acumulado()//self.valor)

    def get_alert(self) -> bool:
        # Verifica si el saldo es insuficiente
        if self.total_gastado() > self.get_acumulado():
            return True  # Se dispara la alerta

        # Verifica si el número de usos es mayor o igual a 5
        if len(self.get_uses_list()) >= 5:
            return True  # Se dispara la alerta

        # Si no hay alertas
        return False

    def __str__(self):
        return str(self.valor)

    def save(self, *args, **kwargs):
        self.descuento_decimal = self.valor * self.descuento / 100
        super().save(*args, **kwargs)

class PagoQuerySet(QuerySet):
    def by_user(self, user):
        return self.filter(usuario=user)
    
    def pago_by_id(self, id_operador):
        return self.filter(prepago__socio__operador__id=id_operador)
    
    def pago_by_date(self, fechaDesde):
        return self.filter(fecha__date=fechaDesde)
    
    def pago_by_date_range(self, fechaDesde, fechaHasta):
        return self.filter(fecha__date__gte=fechaDesde, fecha__date__lte=fechaHasta)

class PagoManager(Manager):
    def get_queryset(self):
        return PagoQuerySet(self.model, using=self._db)
    
    def by_user(self, user):
        return self.get_queryset().by_user(user)
    
    def pago_by_id(self, id):
        return self.get_queryset().pago_by_id(id)
    
    def pago_by_date(self, fechaDesde):
        return self.get_queryset().pago_by_date(fechaDesde)
    
    def pago_by_date_range(self, fechaDesde, fechaHasta):
        return self.get_queryset().pago_by_date_range(fechaDesde, fechaHasta)

class Pago(Model):
    prepago = ForeignKey(Prepago, on_delete=CASCADE)
    monto = FloatField()
    fecha = DateTimeField(default=get_today)
    usuario = ForeignKey(User, on_delete=CASCADE)
    timestamp = DateTimeField(auto_now_add=True)

    objects = PagoManager()

    def get_nombre_socio(self):
        return str(self.prepago.socio)
    
    def __str__(self):
        return str(self.monto)

class TransferenciaPP(Model):
    pago = OneToOneField(Pago, on_delete=CASCADE, related_name='transferenciapp')
    inserted_on = DateField(auto_now_add=True)
    edited_on = DateField(auto_now=True)

    def usuario(self):
        return str(self.pago.usuario)

    def socio(self):
        return str(self.pago.prepago.socio)

    def __str__(self):
        return str(self.pago.prepago.socio) #type: ignore