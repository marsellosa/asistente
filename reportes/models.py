from django.db.models import * # type: ignore
from django.conf import settings
from django.db.models.query import QuerySet
from operadores.models import Operador

Usuario = settings.AUTH_USER_MODEL

class IngresoTipo(TextChoices):

    SOBREROJO = 'SR', 'Sobre Rojo'
    INSUMOS = 'IN', 'Insumos'
    MANTENIMIENTO = 'MT', 'Mantenimiento'

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
    
    monto = FloatField()
    operador = ForeignKey(Operador, on_delete=CASCADE)
    tipo_ingreso = CharField(max_length=2, choices=IngresoTipo.choices, default=IngresoTipo.SOBREROJO)
    detalle = CharField(max_length=255, blank=True, null=True)
    usuario = ForeignKey(Usuario, on_delete=CASCADE)
    inserted_on = DateTimeField(auto_now_add=True)
    updated_on = DateTimeField(auto_now=True)

    objects = IngresoManager()

    def __str__(self):
        return str(self.monto)

