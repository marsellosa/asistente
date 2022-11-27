from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from recetas.models import *
from recetas.utils import number_str_to_float
from productos.models import Categoria

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
        self.receta_ingrediente_herbal_a = RecetaIngredienteHerbal.objects.create(
            receta = self.recipe_a,
            categoria = self.categoria_a,
            cantidad = '1 1/2',
            unidad = 'kilo',
        )

    def test_user_count(self):
        qs = User.objects.all()
        self.assertEqual(qs.count(), 1)

    def test_user_recipe_reverse_count(self):
        user = self.user_a
        qs = user.receta_set.all()
        self.assertEqual(qs.count(), 2)

    def test_user_recipe_forward_count(self):
        user = self.user_a
        qs = Receta.objects.filter(usuario=user)
        self.assertEqual(qs.count(), 2)

    def test_recipe_ingredient_reverse_count(self):
        recipe = self.recipe_a
        qs = recipe.recetaingrediente_set.all()
        self.assertEqual(qs.count(), 2)
    
    def test_recipe_ingredient_forward_count(self):
        recipe = self.recipe_a
        qs = RecetaIngrediente.objects.filter(receta=recipe)
        self.assertEqual(qs.count(), 2)

    def test_user_two_level_relation(self):
        user = self.user_a
        qs = RecetaIngrediente.objects.filter(receta__usuario=user)
        self.assertEqual(qs.count(), 2)

    def test_recipe_ingredient_herbal_reverse_count(self):
        recipe = self.recipe_a
        qs = recipe.recetaingredienteherbal_set.all()
        self.assertEqual(qs.count(), 1)

    def test_unit_measure_validation(self):
        valid_unit = 'gr'
        ingredient = RecetaIngrediente(
            receta = self.recipe_a,
            nombre = 'Nuevo',
            cantidad = 10,
            unidad = valid_unit
        )
        ingredient.full_clean()

    def test_unit_measure_validation_error(self):
        invalid_units = ['nada', 'adfav']
        with self.assertRaises(ValidationError):
            for unit in invalid_units:
                ingredient = RecetaIngrediente(
                    receta = self.recipe_a,
                    nombre = 'Nuevo',
                    cantidad = 10,
                    unidad = unit
                )
                ingredient.full_clean()

    def test_cantidad_decimal(self):
        self.assertIsNotNone(self.receta_ingrediente_a.cantidad_decimal)
        self.assertIsNone(self.receta_ingrediente_b.cantidad_decimal)