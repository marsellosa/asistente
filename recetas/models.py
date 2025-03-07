from typing import List, Optional
from django.db.models import * #type: ignore
from django.conf import settings
from django.urls import reverse
from productos.models import Categoria, Detalles, PrecioDistribuidor, PrecioClientePreferente
from recetas.validators import validar_unidad_de_medida, todo_a_gramos
from recetas.utils import get_float_for_save

class RecetaQuerySet(QuerySet):
    def search(self, query=None):
        if query is None or query == "":
            return self.none()
        lookups = (
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query) | 
            Q(instrucciones__icontains=query)
        )

        return self.filter(lookups)

class RecetaManager(Manager):
    def get_queryset(self):
        return RecetaQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset().search(query=query)

class Receta(Model):

    usuario = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    nombre = CharField(max_length=220)
    descripcion = TextField(blank=True, null=True)
    instrucciones = TextField(blank=True, null=True)
    precio_publico = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    timestamp = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    active = BooleanField(default=True)

    objects = RecetaManager()

    @property
    def titulo(self):
        return self.nombre

    @property
    def get_cart_points(self):
        total_puntos = self.get_herbal_ingredient_children().aggregate(
            total=Sum(self.get_vol_points())
        )['total'] or 0
        return round(total_puntos, 2)

    @property
    def get_total_receta(self) -> Optional[float]:
        """
        Calcula el costo total de la receta sumando los costos de ingredientes herbales y no herbales.

        Returns:
            float: El costo total de la receta, redondeado a dos decimales.
            None: Si no se puede calcular debido a datos insuficientes o errores.
        """
        try:
            # Obtener los ingredientes herbales y no herbales
            herbal_ingredients = self.get_herbal_ingredient_children()
            non_herbal_ingredients = self.get_ingredients_children()

            if not isinstance(herbal_ingredients, (list, QuerySet)) or not isinstance(non_herbal_ingredients, (list, QuerySet)):
                raise ValueError("Los métodos auxiliares deben devolver listas o QuerySets.")

            # Calcular el costo total de ingredientes herbales
            total_herbal = sum(
                getattr(ingrediente, 'get_total', lambda: 0)() for ingrediente in herbal_ingredients
            )

            # Calcular el costo total de ingredientes no herbales
            total_no_herbal = sum(
                getattr(ingrediente, 'get_costo', lambda: 0)() for ingrediente in non_herbal_ingredients
            )

            # Sumar ambos totales y redondear el resultado final
            total_receta = total_herbal + total_no_herbal
            return round(total_receta, 2)

        except (AttributeError, TypeError, ValueError) as e:
            # Manejar errores y devolver None si ocurre algún problema
            print(f"Error al calcular el costo total de la receta: {e}")
            return None
    
    @property
    def get_sobre_rojo(self):
        sobre_rojo = round(sum([ingrediente.get_costo() for ingrediente in self.get_herbal_ingredient_children()]), 2)
        # print(f"get_sobre_rojo: {sobre_rojo}")
        return sobre_rojo

    @property
    def get_insumos(self):
        try:
            insumos = round(sum([ingrediente.get_costo() for ingrediente in self.get_ingredients_children()]), 2)
        except:
            insumos = 0
        # print(f"get_insumos (en model): {insumos}")
        return insumos

    @property
    def get_costo_receta(self):
        try:
            costo = round(sum([self.get_sobre_rojo, self.get_insumos]), 2)
        except:
            costo = 0
        # print(f"get_costo_receta (en model): {costo}")
        return costo

    def get_absolute_url(self):
        return reverse('recetas:detail', kwargs={'id': self.pk})

    def get_edit_url(self):
        return reverse('recetas:update', kwargs={'id': self.pk})

    def get_delete_url(self):
        return reverse('recetas:delete', kwargs={'id': self.pk})

    def get_crud_url(self):
        return reverse('recetas:crud', kwargs={'id': self.pk})

    def get_ingredients_children(self):
        return self.recetaingrediente_set.all() #type: ignore

    def get_herbal_ingredient_children(self) -> QuerySet:
        """
        Devuelve todos los ingredientes herbales relacionados con esta receta.

        Returns:
            QuerySet: Un QuerySet que contiene todos los objetos RecetaIngredienteHerbal
                      relacionados con esta receta.
        """
        try:
            # Acceder a la relación inversa para obtener los ingredientes herbales
            return self.recetaingredienteherbal_set.all()
        except AttributeError as e:
            print(f"Error al acceder a los ingredientes herbales: {e}")
            return []
 
    def __str__(self):
        return self.nombre
    
class Ingrediente(Model):
    nombre = CharField(max_length=64)
    descripcion = TextField(blank=True, null=True)
    timestamp = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre

class RecetaIngrediente(Model):
    receta = ForeignKey(Receta, on_delete=CASCADE)
    ingrediente = ForeignKey(Ingrediente, on_delete=CASCADE, null=True)
    descripcion = TextField(blank=True, null=True)
    cantidad = CharField(max_length=50)
    cantidad_decimal = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    unidad = CharField(max_length=50, validators=[validar_unidad_de_medida])
    timestamp = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    active = BooleanField(default=True)

    def get_absolute_url(self):
        return self.receta.get_absolute_url()

    def _kwargs(self):
        return {
            'parent_id' : self.receta.pk,
            'id'        : self.pk
        }

    def get_costo(self):
        try:
            ingrediente = self.ingrediente.costoingrediente_set.filter(active=True).first() #type:ignore
            precio = round(self.cantidad_decimal * ingrediente.precio / ingrediente.cantidad_decimal, 2) #type:ignore
        except:
            precio = 0
        # print(precio)
        return precio

    def get_delete_url(self):
        return reverse('recetas:ingredient-delete', kwargs=self._kwargs())
    
    def get_hx_edit_url(self):
        return reverse('recetas:hx-ingredient-detail', kwargs=self._kwargs())

    def save(self, *args, **kwargs):
        valor = get_float_for_save(self.cantidad)
        self.cantidad_decimal, self.unidad = todo_a_gramos(valor, self.unidad)
        self.cantidad = self.cantidad_decimal
        super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.ingrediente)
    
class CostoIngrediente(Model):
    
    ingrediente = ForeignKey(Ingrediente, on_delete=CASCADE, null=True)
    precio = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    descripcion = TextField(blank=True, null=True)
    cantidad = CharField(max_length=50)
    cantidad_decimal = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    unidad = CharField(max_length=50, validators=[validar_unidad_de_medida])
    timestamp = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    active = BooleanField(default=True)

    def save(self, *args, **kwargs):
        valor = get_float_for_save(self.cantidad)
        self.cantidad_decimal, self.unidad = todo_a_gramos(valor, self.unidad)
        self.cantidad = self.cantidad_decimal
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.ingrediente)

class RecetaIngredienteHerbal(Model):
    receta = ForeignKey(Receta, on_delete=CASCADE)
    categoria = ForeignKey(Categoria, on_delete=CASCADE)
    descripcion = TextField(blank=True, null=True)
    cantidad = CharField(max_length=50)
    cantidad_decimal = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    unidad = CharField(max_length=50, validators=[validar_unidad_de_medida])
    timestamp = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    active = BooleanField(default=True)

    @property
    def nombre(self):
        return self.categoria

    def save(self, *args, **kwargs):
        valor = get_float_for_save(self.cantidad)
        self.cantidad_decimal, self.unidad = todo_a_gramos(valor, self.unidad)
        self.cantidad = self.cantidad_decimal
        super().save(*args, **kwargs)

    def get_vol_points(self):
        peso_total = Detalles.objects.filter(categoria=self.categoria, activo=True).first().cantidad_decimal #type: ignore
        puntos = round(self.categoria.puntos_volumen * self.cantidad_decimal / peso_total, 2)  # type: ignore
        return puntos

    def get_total(self):
        # sumatoria de ingredientes herbales segun su precio al publico
        precio = self.get_costo(nivel='Cliente')  # type: ignore
        # precio = round(self.categoria.porcion.precio * self.cantidad_decimal / self.categoria.porcion.cantidad_decimal, 2)  # type: ignore
        return precio
    

    def get_costo(self, nivel: str = 'Mayorista') -> Optional[float]:
        """
        Calcula el costo basado en el nivel de distribución especificado.

        Args:
            nivel (str): El nivel de distribución ('Mayorista', 'Productor Calificado', etc.).

        Returns:
            float: El costo calculado, redondeado a dos decimales.
            None: Si no se puede calcular debido a datos insuficientes.
        """
        
        if nivel == 'Cliente':
            obj = PrecioClientePreferente.objects.filter(
                categoria=self.categoria, activo=True
                ).order_by("-inserted_on").first()
            nivel_precio_map = {
                'Cliente': obj.cliente,
            }
        else:
            # Obtener el registro más reciente de precios para la categoría
            obj = PrecioDistribuidor.objects.filter(
                categoria=self.categoria, activo=True
            ).order_by("-inserted_on").first()

            # Mapeo de niveles a campos de precios
            nivel_precio_map = {
                'Mayorista': obj.mayorista,
                'Productor Calificado': obj.productor_calificado,
                'Consultor Mayor': obj.consultor_mayor,
                'Distribuidor': obj.distribuidor,
            }

        if not obj:
                # No se encontró un registro de precios activo
                return None

        # Obtener el precio correspondiente al nivel
        precio = nivel_precio_map.get(nivel)
        if precio is None:
            # Nivel no válido
            return None

        # Obtener la cantidad total desde Detalles
        detalle = Detalles.objects.filter(categoria=self.categoria).first()
        if not detalle or detalle.cantidad_decimal == 0:
            # No se encontraron detalles válidos o cantidad_decimal es cero
            return None

        cant_total = detalle.cantidad_decimal

        # Calcular el costo
        try:
            costo = round(precio * self.cantidad_decimal / cant_total, 2)
            return costo
        except (TypeError, ZeroDivisionError):
            # Manejar errores de tipo o división por cero
            return None

    def _kwargs(self):
        return {
            'parent_id' : self.receta.pk,
            'id'        : self.pk
        }

    def get_hx_edit_url(self):
        return reverse('recetas:hx-herbal-ingredient-detail', kwargs=self._kwargs())

    def get_delete_url(self):
        return reverse('recetas:herbal-ingredient-delete', kwargs=self._kwargs())

    def __str__(self):
        return str(self.categoria)