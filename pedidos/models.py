from django.db.models import * # type: ignore
from django.conf import settings
from django.urls import reverse
from productos.models import Categoria, Detalles, PrecioDistribuidor, PrecioClientePreferente
from socios.models import Operador
import datetime

User = settings.AUTH_USER_MODEL

class PedidoStatus(TextChoices):

    ENTREGADO = 'e', 'Entregado'
    CANCELADO = 'c', 'Cancelado'
    PENDIENTE = 'p', 'Pendiente'
    VENCIDO = 'v', 'Vencido'

class PedidoQuerySet(QuerySet):

    def by_user_id(self, user_id):
        return self.filter(user_id=user_id)

    def by_usuario(self, usuario):
        return self.filter(usuario=usuario)

    def by_operador(self, operador):
        return self.filter(operador=operador)

    def by_operador_id(self, operador_id):
        return self.filter(operador_id=operador_id)

    def by_pedidos_entregados(self, operador_id):
        return self.filter(operador_id=operador_id, status=PedidoStatus.ENTREGADO)

    def candelado(self):
        return self.filter(status=PedidoStatus.CANCELADO)
        
    def entregado(self):
        return self.filter(status=PedidoStatus.ENTREGADO)

    def pendiente(self):
        return self.filter(status=PedidoStatus.PENDIENTE)

    def vencido(self):
        return self.filter(status=PedidoStatus.VENCIDO)

class PedidoManager(Manager):
    def get_queryset(self):
        return PedidoQuerySet(self.model, using=self._db)

    def by_operador(self, operador):
        return self.get_queryset().by_operador(operador)

    def get_pedidos_entregados(self, operador):
        return self.get_queryset().by_pedidos_entregados(operador)

class Pedido(Model):
    
    usuario = ForeignKey(User, on_delete=CASCADE)
    operador = ForeignKey(Operador, on_delete=CASCADE)
    timestamp = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    status = CharField(max_length=1, choices=PedidoStatus.choices, default=PedidoStatus.PENDIENTE)
    pedido_id = CharField(max_length=200)
    total_final = CharField(max_length=10, null=True, blank=True)

    objects = PedidoManager()

    def get_all_items(self):
        return self.pedidoitem_set.all() # type: ignore

    @property
    def get_cart_total(self):
        pedidoitems = self.pedidoitem_set.all() # type: ignore
        total = round(sum([item.get_total(self.operador.get_nivel_licencia) for item in pedidoitems]), 1)
        return total

    @property
    def get_cart_items(self):
        pedidoitems = self.pedidoitem_set.all() # type: ignore
        total = sum([item.cantidad for item in pedidoitems])
        return total

    @property
    def get_cart_points(self):
        pedidoitems = self.pedidoitem_set.all() # type: ignore
        total = round(sum([item.get_vol_points for item in pedidoitems]), 2)
        return total

    def get_absolute_url(self):
        return reverse("pedidos:detail", kwargs={"id": self.pk})

    # def get_total_comprado(self):
    #     return round(sum([self.get_total_comprado()]), 1)

    def save(self, *args, **kwargs):
        self.pedido_id = datetime.datetime.now().timestamp()
        if self.status == PedidoStatus.ENTREGADO:
            self.total_final = self.get_cart_total
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.operador)

class PedidoItem(Model):

    pedido = ForeignKey(Pedido, on_delete=CASCADE)
    categoria = ForeignKey(Categoria, on_delete=CASCADE, null=True)
    detalles = ForeignKey(Detalles, on_delete=CASCADE)
    cantidad = IntegerField(default=1)
    timestamp = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def get_total(self, nivel='Mayorista'):
        precio_dist = PrecioDistribuidor.objects.filter(categoria=self.categoria, activo=True).order_by('-inserted_on').first()
        precio_clip = PrecioClientePreferente.objects.filter(categoria=self.categoria, activo=True).order_by('-inserted_on').first()

        if nivel == 'Mayorista':
            precio = precio_dist.mayorista # type: ignore
        elif nivel == 'Productor Calificado':
            precio = precio_dist.productor_calificado # type: ignore
        elif nivel == 'Consultor Mayor':
            precio = precio_dist.consultor_mayor # type: ignore
        elif nivel == 'Distribuidor':
            precio = precio_dist.distribuidor # type: ignore
        elif nivel == 'Oro':
            precio = precio_clip.oro # type: ignore
        elif nivel == 'Plata':
            precio = precio_clip.plata # type: ignore
        elif nivel == 'Bronce':
            precio = precio_clip.bronce # type: ignore
        elif nivel == 'Cliente':
            precio = precio_clip.cliente # type: ignore

        total = precio * self.cantidad # type: ignore

        return total

    @property
    def get_vol_points(self):
        puntos = round(self.categoria.puntos_volumen * self.cantidad, 2) # type: ignore
        return puntos

    def get_delete_url(self):
        return reverse('pedidos:hx-delete-item', kwargs={'pedido_id': self.pedido.pk, 'id': self.pk})

    def __str__(self):
        return str(self.pedido)