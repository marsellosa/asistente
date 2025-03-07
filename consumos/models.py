from django.db.models import * #type:ignore
from django.db.models.query import QuerySet #type:ignore
from comanda.models import Comanda

class ConsumoQuerySet(QuerySet):

    def qr_by_date(self, fechaDesde):
        return self.filter(comanda__fecha=fechaDesde, transferencia__isnull=False)

    def by_user_date_range(self, id_usuario, fechaDesde, fechaHasta):
        return self.filter(comanda__usuario__id=id_usuario, comanda__fecha__gte=fechaDesde, comanda__fecha__lte=fechaHasta).order_by('-comanda__fecha')
    
    def by_date_range(self, fechaDesde, fechaHasta):
        return self.filter(comanda__fecha__gte=fechaDesde, comanda__fecha__lte=fechaHasta).order_by('-comanda__fecha')

    def by_user(self, usuario):
        return self.filter(comanda__usuario=usuario).order_by('-comanda__fecha')
    
    def by_date(self, fecha):
        return self.filter(comanda__fecha=fecha).order_by('-inserted_on')

    def by_id_operador(self, id_operador):
        return self.filter(comanda__socio__operador__id=id_operador).order_by('-comanda__fecha')

class ConsumoManager(Manager):
    def get_queryset(self):
        return ConsumoQuerySet(self.model, using=self.db)
        
    def by_id_operador(self, id_operador):
        return self.get_queryset().by_id_operador(id_operador)
    
    def by_user(self, usuario):
        return self.get_queryset().by_user(usuario)
    
    def by_date(self, fecha):
        return self.get_queryset().by_date(fecha)
    
    def by_user_date_range(self, id_usuario, fechaDesde, fechaHasta):
        return self.get_queryset().by_user_date_range(id_usuario, fechaDesde, fechaHasta)
    
    def by_date_range(self, fechaDesde, fechaHasta):
        return self.get_queryset().by_date_range(fechaDesde, fechaHasta)

class Consumo(Model):
    comanda = OneToOneField(Comanda, on_delete=CASCADE, null=True, blank=True)
    total_consumido = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    sobre_rojo = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    mayoreo = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    insumos = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    descuento = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    sobre_verde = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    efectivo = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    puntos_volumen = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    inserted_on = DateField(auto_now_add=True)
    edited_on = DateField(auto_now=True)

    
    objects = ConsumoManager()

    def __str__(self):
        return str(self.comanda)
    
class Transferencia(Model):
    consumo = OneToOneField(Consumo, on_delete=CASCADE, related_name='transferencia')
    inserted_on = DateField(auto_now_add=True)
    edited_on = DateField(auto_now=True)

    def get_monto(self):
        return self.consumo.efectivo

    def __str__(self):
        return str(self.consumo.comanda.socio) #type: ignore