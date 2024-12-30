from django.db.models import *
from django.conf import settings
from django.urls import reverse
from django.core.cache import cache
from django.utils.timezone import now
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q
from itertools import chain
from main.models import Settings
from recetas.models import Receta
from socios.models import Socio
from prepagos.models import Prepago

User = settings.AUTH_USER_MODEL


def get_setting_value(name, default=0):
    """Utility to fetch settings with caching."""
    cache_key = f"setting_{name}"
    value = cache.get(cache_key)
    if value is None:
        try:
            value = int(Settings.objects.get(nombre=name).valor)
        except Settings.DoesNotExist:
            value = default
        cache.set(cache_key, value, timeout=3600)  # Cache for an hour
    return value


class ComandaStatus(TextChoices):
    ENTREGADO = 'e', 'Entregado'
    CANCELADO = 'c', 'Cancelado'
    PENDIENTE = 'p', 'Pendiente'
    VENCIDO = 'v', 'Vencido'


class ComandaQuerySet(QuerySet):
    def by_user_id(self, user_id):
        return self.filter(id=user_id)

    def by_user(self, usuario):
        return self.filter(usuario=usuario)

    def cancelado(self):
        return self.filter(status=ComandaStatus.CANCELADO)

    def entregado(self):
        return self.filter(status=ComandaStatus.ENTREGADO)

    def pendiente(self):
        return self.filter(status=ComandaStatus.PENDIENTE)

    def vencido(self):
        return self.filter(status=ComandaStatus.VENCIDO)

    def annotated_totals(self):
        return self.annotate(
            cart_total=Sum(F('comandaitem__cantidad') * F('comandaitem__receta__precio_publico')),
            cart_points=Sum(F('comandaitem__cantidad') * F('comandaitem__receta__get_cart_points')),
        )


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
        return reverse('comanda:hx-crud-comanda-item', kwargs={'id_comanda': self.pk, 'id_receta': None})

    @property
    def get_uniq_prepagos_list(self):
        socio_prepagos = self.socio.prepago_set.filter(activo=True)
        comanda_prepagos = self.prepago.all()
        return list(socio_prepagos.union(comanda_prepagos))

    @property
    def get_total_descuento(self):
        return round(sum(item.descuento_decimal for item in self.get_cart_prepagos), 2)

    @property
    def get_cart_prepagos(self):
        return self.prepago.all()

    @property
    def get_sobre_rojo(self):
        costos = sum(item.get_sobre_rojo for item in self.get_all_items())
        porciento = get_setting_value('inversion', 10)
        re_inversion = self.porcentaje(costos, porciento)
        return round(costos + re_inversion, 2)

    @property
    def get_cart_total(self):
        return self.get_all_items().aggregate(
            total=Sum(F('cantidad') * F('receta__precio_publico'))
        )['total'] or 0

    @property
    def get_mantenimiento(self):
        mant = get_setting_value('mantenimiento', 10)
        return self.porcentaje(self.get_cart_total, mant)

    @property
    def get_insumos(self):
        total = sum(item.get_insumos for item in self.get_all_items())
        insumos = get_setting_value('insumos', 1)
        return total + insumos

    @property
    def get_cart_count_items(self):
        return self.get_all_items().aggregate(
            total=Sum('cantidad')
        )['total'] or 0

    @property
    def get_cart_points(self):
        return round(sum(item.get_puntos for item in self.get_all_items()), 2)

    @property
    def get_cart_cash(self):
        if self.is_operador():
            efectivo = round(self.get_mantenimiento + self.get_insumos + self.get_sobre_rojo, 2)
        else:
            efectivo = self.get_cart_total - sum(prepago.valor for prepago in self.prepago.all())
        return max(efectivo, 0)

    @property
    def get_sobre_verde(self):
        if self.is_operador():
            return 0
        costos = round(sum([self.get_sobre_rojo, self.get_total_descuento, self.get_insumos, self.get_mantenimiento]), 2)
        return round(self.get_cart_total - costos, 2)

    def is_operador(self):
        try:
            return self.socio.persona.licencia.operador
        except AttributeError:
            return False

    def get_all_items(self):
        return self.comandaitem_set.all()

    def porcentaje(self, total, porciento):
        return total * porciento / 100

    def __str__(self):
        return str(self.socio)

    class Meta:
        constraints = [
            CheckConstraint(check=~Q(status=''), name='status_not_empty'),
        ]


class ComandaItem(Model):
    comanda = ForeignKey(Comanda, on_delete=CASCADE)
    receta = ForeignKey(Receta, on_delete=SET_NULL, null=True, blank=True)
    cantidad = IntegerField(default=1, blank=True, null=True)
    timestamp = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    @property
    def get_puntos(self):
        try:
            return round(self.cantidad * self.receta.get_cart_points, 2)
        except AttributeError:
            return 0

    @property
    def get_total(self):
        try:
            return round(self.cantidad * self.receta.precio_publico, 1)
        except AttributeError:
            return 0

    @property
    def get_costo(self):
        try:
            return round(self.cantidad * self.receta.get_costo_receta, 1)
        except AttributeError:
            return 0

    @property
    def get_insumos(self):
        try:
            return round(self.cantidad * self.receta.get_insumos, 1)
        except AttributeError:
            return 0

    @property
    def get_sobre_rojo(self):
        try:
            return round(self.cantidad * self.receta.get_sobre_rojo, 1)
        except AttributeError:
            return 0

    def get_crud_url(self):
        return reverse('comanda:hx-crud-comanda-item', kwargs={'id_receta': self.pk, 'id_comanda': self.comanda.pk})

    def get_edit_url(self):
        return reverse('comanda:hx-edit-item', kwargs={'id_comanda_item': self.pk})

    def __str__(self):
        return str(self.receta)
