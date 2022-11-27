from django.contrib.auth import get_user_model
from django.test import TestCase
from recetas.models import *
from productos.models import Categoria
from pedidos.models import Pedido, PedidoStatus
from operadores.models import Operador
from persona.models import Licencia, Persona
from socios.models import Socio

User = get_user_model()

class UserTestCase(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user('llosa', password='abc123')

    def test_user_pw(self):
        checked = self.user_a.check_password('abc123')
        self.assertTrue(checked)

class RecetaTestCase(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user('llosa', password='abc123')
        self.persona = Persona.objects.create(
            nombre = 'Marcelo',
            apellido = 'Llosa'
        )
        self.socio = Socio.objects.create(
            persona = self.persona,
        )
        self.licencia = Licencia.objects.create(
            persona = self.persona,
        )
        self.operador = Operador.objects.create(
            licencia = self.licencia,
        )
        self.operador_id = self.operador.id
        
        self.recipe_a = Receta.objects.create(
            nombre = 'Pollo Frito',
            usuario = self.user_a
        )
        self.recipe_b = Receta.objects.create(
            nombre = 'Carne Asada',
            usuario = self.user_a
        )
        self.receta_ingrediente_a = RecetaIngrediente.objects.create(
            receta = self.recipe_a,
            nombre = 'Pollo',
            cantidad = '1 1/2',
            unidad = 'kilo',
        )
        self.receta_ingrediente_b = RecetaIngrediente.objects.create(
            receta = self.recipe_a,
            nombre = 'Pollo',
            cantidad = 'ashvnah',
            unidad = 'kilo',
        )
        # self.categoria_a = Categoria.objects.create(
        #     nombre = 'Croquetas',
        #     puntos_volumen = 0.2,
        #     distribuidor = 0.2,
        #     consultor_mayor = 0.2,
        #     productor_calificado = 0.2,
        #     mayorista = 0.2,
        #     cliente_bs = 0.2,
        #     cliente_sus = 0.2,
        # )
        # self.receta_ingrediente_herbal_a = RecetaIngredienteHerbal.objects.create(
        #     receta = self.recipe_a,
        #     categoria = self.categoria_a,
        #     cantidad = '1 1/2',
        #     unidad = 'kilo',
        # )
        

        self.pedido_a = Pedido.objects.create(
            usuario = self.user_a,
            operador = self.operador,
            status = PedidoStatus.PENDIENTE,
        )
        self.pedido_b = Pedido.objects.create(
            usuario = self.user_a,
            operador = self.operador,
            status = PedidoStatus.ENTREGADO,
        )

    def test_pedidos_por_operador(self):
        qs = Pedido.objects.all().by_operador_id(self.operador_id)
        self.assertEqual(qs.count(), 2)

    def test_pedidos_pendientes(self):
        qs = Pedido.objects.all().pendiente()
        self.assertEqual(qs.count(), 1)

        qs = Pedido.objects.all().by_operador(self.operador).pendiente()
        # qs = Pedido.objects.by_operador(self.operador).pendiente()
        self.assertEqual(qs.count(), 1)

    def test_pedidos_entregados(self):
        qs = Pedido.objects.all().entregado()
        self.assertEqual(qs.count(), 1)

        qs = Pedido.objects.by_operador(self.operador).entregado()
        self.assertEqual(qs.count(), 1)