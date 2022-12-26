
from django.db.models import * #type: ignore
from recetas.validators import validar_unidad_de_medida
from recetas.utils import get_float_for_save

class CategoriaQuerySet(QuerySet):
    def search(self, query=None):
        if query is None or query == "":
            return self.none()
        lookups = (
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(palabras_clave__icontains=query)
        )
        
        return self.filter(lookups, activo=True)

    def interna(self):
        return self.filter(tipo='interna', activo=True)

    def externa(self):
        return self.filter(tipo='externa', activo=True)

class CategoriaManager(Manager):
    def get_queryset(self):
        return CategoriaQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset().search(query=query)

    def interna(self):
        return self.get_queryset().interna

    def externa(self):
        return self.get_queryset().externa

class Categoria(Model):
    default_option = 'interna'
    categoria_opciones = [
        ('hmp', 'HMP'),
        ('nutricion', (
                (default_option, 'INTERNA'),
                ('externa', 'EXTERNA')
            )
        ),
        ('promocion', (
                ('utensilios', 'UTENSILIOS'),
                ('literatura', 'LITERATURA')
            )
        )
    ]
    default_detail = "{}\nCantidad: {}\nPV: {}\nDistribuidor - 25% : {:>10} Bs.\nConsultor - 35% : {:>14} Bs.\nConstructor - 42% : {:>10} Bs.\nMayorista - 50% : {:>14} Bs."

    nombre = CharField(max_length=150)
    image_url = CharField(max_length=255, blank=True, null=True)
    descripcion = CharField(max_length=255, blank=True, null=True)
    detalle = TextField(blank=True, null=True, default=default_detail)
    cantidad = IntegerField(default=1)
    puntos_volumen = FloatField(max_length=10)
    activo = BooleanField(default=True)
    inserted_on = DateField(auto_now_add=True)
    edited_on = DateField(auto_now=True)
    palabras_clave = TextField(blank=True, null=True)
    tipo = CharField(max_length=32, choices=categoria_opciones, default=default_option)

    objects = CategoriaManager()

    class Meta:
        verbose_name_plural = "Categorias"

    @property
    def precios_distribuidor(self):
        qs = self.preciodistribuidor_set.filter(activo=True).first() #type: ignore
        # print(f"qs: {qs}")
        return qs

    def __str__(self):
        return self.nombre
    
    def get_details(self):
        return self.detalles_set.all() #type: ignore

class PrecioDistribuidor(Model):
    categoria = ForeignKey(Categoria, on_delete=CASCADE)
    distribuidor = FloatField(max_length=10)
    consultor_mayor = FloatField(max_length=10)
    productor_calificado = FloatField(max_length=10)
    mayorista = FloatField(max_length=10)
    activo = BooleanField(default=True)
    inserted_on = DateField(auto_now_add=True)
    edited_on = DateField(auto_now=True)

    def __str__(self):
        return str(self.categoria)

class PrecioClientePreferente(Model):
    categoria = ForeignKey(Categoria, on_delete=CASCADE)
    oro = FloatField(max_length=10)
    plata = FloatField(max_length=10)
    bronce = FloatField(max_length=10)
    cliente = FloatField(max_length=10)
    activo = BooleanField(default=True)
    inserted_on = DateField(auto_now_add=True)
    edited_on = DateField(auto_now=True)

    def __str__(self):
        return str(self.categoria)
    

class Sabor(Model):

    categoria = ForeignKey('Categoria', on_delete=SET_NULL, null=True)
    nombre = CharField(max_length=64)
    descripcion = CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Sabores'

    def __str__(self):
        return self.nombre
    
class Pais(Model):

    nombre = CharField(max_length=64, unique=True)

    class Meta:
        verbose_name_plural = 'Paises'

    def __str__(self):
        return self.nombre

class DetallesQuerySet(QuerySet):
    def search(self, query=None):
        if query is None or query == "":
            return self.none()
        lookups = (
            Q(categoria__nombre__icontains=query) |
            Q(sabor__icontains=query) |
            Q(descripcion__icontains=query)
        )
        
        return self.filter(lookups, activo=True)

class DetallesManager(Manager):
    def get_queryset(self):
        return DetallesQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset().search(query=query)

class Detalles(Model):

    categoria = ForeignKey(Categoria, on_delete=CASCADE, null=True)
    pais = ForeignKey('Pais', on_delete=SET_NULL, null=True, blank=True)
    sku = CharField(max_length=8)
    sabor = CharField(max_length=64)
    descripcion = CharField(max_length=255, blank=True, null=True)
    codigo_barras = CharField(max_length=16, blank=True, null=True)
    activo = BooleanField(default=True)
    cantidad = CharField(max_length=50)
    cantidad_decimal = FloatField(blank=True, null=True)
    unidad = CharField(max_length=50, validators=[validar_unidad_de_medida])

    objects = DetallesManager()
    
    def save(self, *args, **kwargs):
        self.cantidad_decimal = get_float_for_save(self.cantidad)
        super().save(*args, **kwargs)
    
    class Meta:
        managed = True
        verbose_name = 'Detalle'
        verbose_name_plural = 'Detalles'

    def __str__(self):
        return self.sabor
    
class Porcion(Model):

    categoria = OneToOneField(Categoria, on_delete=CASCADE)    
    precio = FloatField()
    cantidad = CharField(max_length=50)
    cantidad_decimal = FloatField(blank=True, null=True)
    unidad = CharField(max_length=50, validators=[validar_unidad_de_medida])
    
    def get_costo_porcion(self, nivel='Mayorista'):
        if nivel == 'Mayorista':
            precio = PrecioDistribuidor.objects.filter(categoria=self.categoria).first().mayorista #type: ignore
        elif nivel == 'Productor Calificado':
            precio = PrecioDistribuidor.objects.filter(categoria=self.categoria).first().productor_calificado #type: ignore
        elif nivel == 'Consultor Mayor':
            precio = PrecioDistribuidor.objects.filter(categoria=self.categoria).first().consultor_mayor #type: ignore
        elif nivel == 'Distribuidor':
            precio = PrecioDistribuidor.objects.filter(categoria=self.categoria).first().distribuidor #type: ignore

        cant_total = Detalles.objects.filter(categoria=self.categoria).first().cantidad_decimal #type: ignore
        costo = self.cantidad_decimal * precio / cant_total #type: ignore
        return costo
    
    def save(self, *args, **kwargs):
        self.cantidad_decimal = get_float_for_save(self.cantidad)
        super().save(*args, **kwargs)

 
    def __str__(self):
        return str(self.categoria)
    


