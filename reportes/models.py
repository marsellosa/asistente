from django.db.models import * # type: ignore
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from operadores.models import Operador
from decimal import Decimal

class IngresoTipo(TextChoices):
    SOBREROJO = 'SR', _('Sobre Rojo')
    INSUMOS = 'IN', _('Insumos')
    MANTENIMIENTO = 'MT', _('Mantenimiento')

class IngresoQuerySet(QuerySet):
    def sobre_rojo(self):
        return self.filter(tipo_ingreso=IngresoTipo.SOBREROJO)
    
    def sobre_rojo_operador(self, operador):
        return self.filter(tipo_ingreso=IngresoTipo.SOBREROJO, operador=operador).order_by('-timestamp')
    
    def insumos(self):
        return self.filter(tipo_ingreso=IngresoTipo.INSUMOS)
    
    def insumos_operador(self, operador):
        return self.filter(tipo_ingreso=IngresoTipo.INSUMOS, operador=operador)

    def mantenimiento(self):
        return self.filter(tipo_ingreso=IngresoTipo.MANTENIMIENTO)
    
    def mantenimiento_operador(self, operador):
        return self.filter(tipo_ingreso=IngresoTipo.MANTENIMIENTO, operador=operador)

class IngresoManager(Manager):
    def get_queryset(self):
        return IngresoQuerySet(self.model, using=self._db)
    
    def sobre_rojo_operador(self, operador):
        return self.get_queryset().sobre_rojo_operador(operador)


class Ingreso(Model):
    
    monto = DecimalField(
        decimal_places=2,
        max_digits=10,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    operador = ForeignKey(Operador, on_delete=CASCADE)
    tipo_ingreso = CharField(
        max_length=2,
        choices=IngresoTipo.choices,
        default=IngresoTipo.SOBREROJO
    )
    detalle = CharField(max_length=255, blank=True)
    usuario = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    objects = IngresoManager()

    def __str__(self):
        return f"Ingreso de {self.monto} ({self.get_tipo_ingreso_display()})"

