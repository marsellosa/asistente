from decimal import Decimal
from django.db.models import * # type: ignore
from django.conf import settings
from django.urls import reverse
from productos.models import Categoria, Detalles, PrecioDistribuidor, PrecioClientePreferente
from socios.models import Operador
import datetime
import logging

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
    total_final = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)

    objects = PedidoManager()

    def get_all_items(self):
        return self.pedidoitem_set.all() # type: ignore

    @property
    def get_cart_total(self) -> Decimal:
        """
        Calcula el costo total de todos los productos
        asociados al pedido, considerando el nivel del operador.
        Returns:
            Decimal: El costo total redondeado a dos decimales.
        """
        try:
            # Determinar el nivel del operador
            nivel_operador = self.operador.get_nivel_licencia  
            # Calcular el costo total de los ingredientes herbales
            costo_total = Decimal('0.00')
            for item in self.get_all_items():
                costo_producto = item.get_total(nivel=nivel_operador)
                if costo_producto is not None:
                    costo_total += Decimal(costo_producto)
            return costo_total
        except Exception as e:
            # Registrar el error
            logging.error(f"Error al calcular get_sobre_rojo: {e}")
            return Decimal('0.00')

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
        return reverse("pedidos:detail", kwargs={"id_pedido": self.pedido_id})

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
        nivel_to_atributo = {
            'Mayorista': ('PrecioDistribuidor', 'mayorista'),
            'Productor Calificado': ('PrecioDistribuidor', 'productor_calificado'),
            'Consultor Mayor': ('PrecioDistribuidor', 'consultor_mayor'),
            'Distribuidor': ('PrecioDistribuidor', 'distribuidor'),
            'Oro': ('PrecioClientePreferente', 'oro'),
            'Plata': ('PrecioClientePreferente', 'plata'),
            'Bronce': ('PrecioClientePreferente', 'bronce'),
            'Cliente': ('PrecioClientePreferente', 'cliente'),
        }
        try:
            nivel = self.pedido.operador.get_nivel_licencia
        except:
            pass

        if nivel not in nivel_to_atributo:
            raise ValueError(f"Nivel '{nivel}' no es válido.")

        modelo, atributo = nivel_to_atributo[nivel]

        if modelo == 'PrecioDistribuidor':
            precio_obj = PrecioDistribuidor.objects.filter(
                categoria=self.categoria, activo=True
            ).order_by('-inserted_on').first()
        elif modelo == 'PrecioClientePreferente':
            precio_obj = PrecioClientePreferente.objects.filter(
                categoria=self.categoria, activo=True
            ).order_by('-inserted_on').first()

        if not precio_obj:
            raise ValueError(f"No se encontró un precio activo para la categoría '{self.categoria}' y nivel '{nivel}'.")

        precio = getattr(precio_obj, atributo, None)
        if precio is None:
            raise ValueError(f"El atributo '{atributo}' no existe o es nulo para el nivel '{nivel}'.")

        total = precio * self.cantidad

        return total

    @property
    def get_vol_points(self):
        puntos = round(self.categoria.puntos_volumen * self.cantidad, 2) # type: ignore
        return puntos

    def get_delete_url(self):
        return reverse('pedidos:hx-delete-item', kwargs={'item_id': self.pk})

    def __str__(self):
        return str(self.pedido)