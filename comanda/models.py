from django.db.models import * # type: ignore
from itertools import chain
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
        return self.filter(id=user_id)

    def by_user(self, usuario):
        return self.filter(usuario=usuario)

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
        return reverse('comanda:hx-crud-comanda-item', kwargs={'id_comanda': self.pk, 'id_receta': None})
    
    @property
    def get_uniq_prepagos_list(self):
        ppagos = list(chain(self.socio.prepago_set.filter(activo=True), self.prepago.all())) #type: ignore
        prepagos_uniq = []
        [prepagos_uniq.append(ppago) for ppago in ppagos if ppago not in prepagos_uniq]
        return prepagos_uniq

    @property
    def get_total_descuento(self):
        try:
            total = round(sum([item.descuento_decimal for item in self.get_cart_prepagos]), 2)
        except:
            total = 0

        return total
    
    @property
    def get_cart_prepagos(self):
        return self.prepago.all()
    
    @property
    def get_sobre_rojo(self):
        costos = sum([item.get_sobre_rojo for item in self.get_all_items()])
        try:
            porciento = float(Settings.objects.get(nombre='inversion').valor)
        except:
            porciento = 10
        re_inversion = self.porcentaje(costos, porciento)
        return round(sum([costos, re_inversion]), 2)

    @property
    def get_cart_total(self):
        total = sum([item.get_total for item in self.get_all_items()])
        return total

    @property
    def get_mantenimiento(self):
        try:
            mant = float(Settings.objects.get(nombre='mantenimiento').valor)
        except:
            mant = 10
    
        return self.porcentaje(self.get_cart_total, mant)

    @property
    def get_insumos(self):
        total = sum([item.get_insumos for item in self.get_all_items()])
        insumos = 0
        if self.get_all_items():
            try:
                insumos = float(Settings.objects.get(nombre='insumos').valor)
            except:
                insumos = 1

        return sum([total, insumos])

    @property
    def get_cart_count_items(self):
        total = sum([item.cantidad for item in self.get_all_items()])
        return total

    @property
    def get_cart_points(self):
        puntos = round(sum([item.get_puntos for item in self.get_all_items()]), 2)
        return puntos
    
    @property
    def get_cart_cash(self):
        if self.is_operador():
            efectivo = round(sum([self.get_mantenimiento, self.get_insumos, self.get_sobre_rojo]), 2)
        else:
            efectivo = self.get_cart_total - sum([prepago.valor for prepago in self.prepago.all()])
        return efectivo
    
    @property
    def get_sobre_verde(self):
        if self.is_operador():
            s_verde = 0
        else:
            costos = round(sum([self.get_sobre_rojo, self.get_total_descuento, self.get_insumos, self.get_mantenimiento]), 2)
            s_verde = round(self.get_cart_total - costos, 2)
        return s_verde
    
    def is_operador(self):
        try:
            licencia = self.socio.persona.licencia.operador # type: ignore
        except:
            licencia = None
        return licencia


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
        try:
            puntos = self.cantidad * self.receta.get_cart_points # type: ignore
        except:
            puntos = 0
        return round(puntos, 2)
    
    @property
    def get_total(self):
        try:
            total = self.cantidad * self.receta.precio_publico # type: ignore
        except:
            total = 0
        # print(f"get_total: %s" % total)
        return round(total, 1)
    
    @property
    def get_costo(self):
        try:
            costo = self.cantidad * self.receta.get_costo_receta # type: ignore
        except:
            costo = 0
        return round(costo, 1)
    
    @property
    def get_insumos(self):
        try:
            costo = self.cantidad * self.receta.get_insumos # type: ignore
        except:
            costo = 0
        return round(costo, 1)

    @property
    def get_sobre_rojo(self):
        try:
            sobre_rojo = self.cantidad * self.receta.get_sobre_rojo #type:ignore
        except:
            sobre_rojo = 0
        return round(sobre_rojo, 1)
    
    def get_crud_url(self):
        return reverse('comanda:hx-crud-comanda-item', kwargs={'id_receta': self.pk, 'id_comanda': self.comanda.pk})
    
    def get_edit_url(self):
        return reverse('comanda:hx-edit-item', kwargs={'id_comanda_item': self.pk})

    def __str__(self):
        return str(self.receta)