from http.client import PRECONDITION_FAILED
from django.contrib.auth import get_user_model
from django.test import TestCase
from productos.models import Categoria, Porcion

User = get_user_model()

class UserTestCase(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user('llosa', password='abc123')

    def test_user_pw(self):
        checked = self.user_a.check_password('abc123')
        self.assertTrue(checked)

class ProductoTestCase(TestCase):
    def setUp(self):
        
        self.categoria_a = Categoria.objects.create(
            nombre = 'Croquetas',
            puntos_volumen = 0.2,
            distribuidor = 0.2,
            consultor_mayor = 0.2,
            productor_calificado = 0.2,
            mayorista = 0.2,
            cliente_bs = 0.2,
            cliente_sus = 0.2,
        )
        self.porcion_a = Porcion.objects.create(
            categoria = self.categoria_a,
            precio = 10,
            medida = 10,
            unidad = 'gr' 
        )

    def test_portion_forward_count(self):
        categoria = self.categoria_a
        qs = categoria.porcion_get.first()
        self.assertEqual(qs.count(), 1)