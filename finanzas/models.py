from django.db.models import *
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from operadores.models import Operador
from reportes.models import Semana
from decimal import Decimal

class MovimientoTipo(TextChoices):
    EGRESO = 'EG', _('Egreso')
    INGRESO = 'IN', _('Ingreso')
    TRANSFERENCIA = 'TR', _('Transferencia')

class SobreTipo(TextChoices):
    SOBREROJO = 'SR', _('Sobre Rojo')
    SOBREVERDE = 'SV', _('Sobre Verde')
    INSUMOS = 'IN', _('Insumos')
    MANTENIMIENTO = 'MT', _('Mantenimiento')

class SobreQuerySet(QuerySet):
    def sobre_rojo(self):
        return self.filter(tipo_movimiento=SobreTipo.SOBREROJO)
    
    def sobre_rojo_operador(self, operador):
        return self.filter(tipo_movimiento=SobreTipo.SOBREROJO, operador=operador).order_by('-timestamp')
    
    def insumos(self):
        return self.filter(tipo_movimiento=SobreTipo.INSUMOS)
    
    def insumos_operador(self, operador):
        return self.filter(tipo_movimiento=SobreTipo.INSUMOS, operador=operador)

    def mantenimiento(self):
        return self.filter(tipo_movimiento=SobreTipo.MANTENIMIENTO)
    
    def mantenimiento_operador(self, operador):
        return self.filter(tipo_movimiento=SobreTipo.MANTENIMIENTO, operador=operador)

class MovimientoManager(Manager):
    def get_queryset(self):
        return SobreQuerySet(self.model, using=self._db)
    
    def sobre_rojo_operador(self, operador):
        return self.get_queryset().sobre_rojo_operador(operador)


class Movimiento(Model):
    
    monto = DecimalField(
        decimal_places=2,
        max_digits=10,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    operador = ForeignKey(Operador, on_delete=CASCADE)
    tipo_sobre = CharField(
        max_length=2,
        choices=SobreTipo.choices,
        default=SobreTipo.SOBREROJO
    )
    tipo_movimiento = CharField(
        max_length=2,
        choices=MovimientoTipo.choices,
        default=MovimientoTipo.INGRESO
    )
    detalle = CharField(max_length=255, blank=True)
    usuario = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    semana = ForeignKey(Semana, on_delete=SET_NULL, null=True, blank=True)

    objects = MovimientoManager()

    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} de {self.monto} ({self.get_tipo_sobre_display()})"


