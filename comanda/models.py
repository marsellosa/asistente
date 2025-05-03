from decimal import Decimal
from django.db.models import *
from django.conf import settings
from django.urls import reverse
from django.core.cache import cache
from django.utils.timezone import now
from django.db.models import Sum, F, Q
from django.db.models.functions import Coalesce
from main.models import Settings
from recetas.models import Receta
from socios.models import Socio
from prepagos.models import Prepago
import logging

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
    def get_sobre_rojo(self) -> Decimal:
        """
        Calcula el costo total de los ingredientes herbales de todas las recetas
        asociadas a la comanda, considerando el nivel del operador.
        Returns:
            Decimal: El costo total redondeado a dos decimales.
        """
        try:
            # Verificar si el socio tiene un operador asociado
            # y si el operador tiene un nivel de licencia
            # Si no hay operador o no tiene nivel, retornar 0
            if not hasattr(self, 'socio') or not hasattr(self.socio, 'operador'):
                return Decimal('0.00')
            
            # Determinar el nivel del operador
            nivel_operador = self.socio.operador.get_nivel_licencia  
            # Calcular el costo total de los ingredientes herbales
            costo_total = Decimal('0.00')
            for item in self.comandaitem_set.select_related('receta').all():
                receta = item.receta
                for ing_herb in receta.get_herbal_ingredient_children():
                    costo_ingrediente = ing_herb.get_costo(nivel=nivel_operador)
                    if costo_ingrediente is not None:
                        costo_total += Decimal(costo_ingrediente)

            # Obtener el porcentaje de reinversión desde Settings
            porciento_inversion = Decimal(get_setting_value('inversion', 10))

            # Calcular la reinversión
            re_inversion = self.porcentaje(costo_total, porciento_inversion)

            # Sumar el costo total y la reinversión
            sobre_rojo_final = (costo_total + re_inversion).quantize(Decimal('0.00'))

            return sobre_rojo_final
        except Exception as e:
            # Registrar el error
            logging.error(f"Error al calcular get_sobre_rojo: {e}")
            return Decimal('0.00')

    # @property
    # def get_cart_total(self):
    #     return self.get_all_items().aggregate(
    #         total=Sum(F('cantidad') * F('receta__precio_publico'))
    #     )['total'] or 0

    @property
    def get_cart_total(self):
        return self.get_all_items().aggregate(
            total=Coalesce(Sum(F('cantidad') * F('receta__precio_publico')), Decimal('0.00'))
        )['total']

    @property
    def get_mantenimiento(self):
        mant = get_setting_value('mantenimiento', 10)
        return self.porcentaje(self.get_cart_total, mant)

    @property
    def get_insumos(self):
        items = self.get_all_items()
        total = sum(item.get_insumos for item in items) if items else 0

        # Obtener el valor de insumos desde Settings
        insumos = get_setting_value('insumos', 0) if items else 0
        total += insumos

        return Decimal(total).quantize(Decimal('0.00'))

    @property
    def get_cart_count_items(self):
        return self.get_all_items().aggregate(
            total=Coalesce(Sum('cantidad'), 0)
        )['total']

    @property
    def get_cart_points(self):
        return round(sum(item.get_puntos for item in self.get_all_items()), 2)

    @property
    def get_cart_cash(self):
        if self.is_operador():
            efectivo = round(self.get_mantenimiento + self.get_insumos + self.get_sobre_rojo, 2)
        else:
            efectivo = self.get_cart_total - sum(prepago.valor for prepago in self.prepago.all())
        return max(Decimal(efectivo).quantize(Decimal('0.00')), Decimal('0.00'))

    @property
    def get_sobre_verde(self):
        """
        Calcula el valor de 'sobre verde' restando los costos totales del total del carrito.
        Returns:
            Decimal: El valor de 'sobre verde', redondeado a dos decimales.
        """
        if self.is_operador():
            return Decimal('0.00')

        # Convertir todos los valores a Decimal y manejar valores nulos
        sobre_rojo = Decimal(self.get_sobre_rojo).quantize(Decimal('0.00'))
        total_descuento = Decimal(self.get_total_descuento).quantize(Decimal('0.00'))
        insumos = Decimal(self.get_insumos).quantize(Decimal('0.00'))
        mantenimiento = Decimal(self.get_mantenimiento).quantize(Decimal('0.00'))
        print(f"Sobre rojo: {sobre_rojo}, Total descuento: {total_descuento}, Insumos: {insumos}, Mantenimiento: {mantenimiento}")
        # Calcular la suma de costos
        costos = (sobre_rojo + total_descuento + insumos + mantenimiento).quantize(Decimal('0.00'))

        # Calcular el valor de 'sobre verde'
        cart_total = Decimal(self.get_cart_total).quantize(Decimal('0.00'))
        sobre_verde = (cart_total - costos).quantize(Decimal('0.00'))

        return sobre_verde

    def is_operador(self):
        try:
            return self.socio.persona.licencia.operador
        except AttributeError:
            return False

    def get_all_items(self):
        return self.comandaitem_set.all()

    def porcentaje(self, total: Decimal, porciento: float) -> Decimal:
        """
        Calcula el porcentaje de un valor dado.
        Args:
            total (Decimal): El valor base.
            porciento (float): El porcentaje a calcular.
        Returns:
            Decimal: El resultado del cálculo, redondeado a dos decimales.
        """
        return (total * Decimal(porciento) / 100).quantize(Decimal('0.00'))

    # def porcentaje(self, total, porciento):
    #     return total * porciento / 100

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
