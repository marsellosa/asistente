from django.db.models import * #type:ignore
from django.db.models.query import QuerySet #type:ignore
from comanda.models import Comanda

class ConsumoQuerySet(QuerySet):

    def by_user(self, id_usuario, fecha):
        return self.filter(comanda__usuario__id=id_usuario, comanda__fecha=fecha)

    def by_id_operador(self, id_operador):
        return self.filter(comanda__socio__operador__id=id_operador)

class ConsumoManager(Manager):
    def get_queryset(self):
        return ConsumoQuerySet(self.model, using=self.db)
        
    def by_id_operador(self, id_operador):
        return self.get_queryset().by_id_operador(id_operador)
    
    def by_user(self, id_usuario, fecha):
        return self.get_queryset().by_user(id_usuario, fecha)

class Consumo(Model):
    comanda = OneToOneField(Comanda, on_delete=CASCADE, null=True, blank=True)
    total_consumido = FloatField(default=0)
    sobre_rojo = FloatField(default=0)
    mayoreo = FloatField(default=0)
    insumos = FloatField(default=0)
    descuento = FloatField(default=0)
    sobre_verde = FloatField(default=0)
    efectivo = FloatField(default=0)
    puntos_volumen = FloatField(default=0)
    inserted_on = DateField(auto_now_add=True)
    edited_on = DateField(auto_now=True)

    objects = ConsumoManager()

    def __str__(self):
        return str(self.comanda)