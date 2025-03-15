
from django.db.models import * #type: ignore
from recetas.validators import validar_unidad_de_medida, todo_a_gramos
from recetas.utils import get_decimal_for_save

class CategoriaQuerySet(QuerySet):
    def search(self, query=None):
        if query is None or query == "":
            return self.none()
        lookups = (
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(palabras_clave__icontains=query) |
            Q(palabrasclave__palabra__icontains=query) |
            Q(detalles__sabor__icontains=query, detalles__activo=True)
        )
        
        return self.filter(lookups, activo=True)

    def interna(self):
        return self.filter(tipo='interna', activo=True).order_by('nombre')

    def externa(self):
        return self.filter(tipo='externa', activo=True).order_by('nombre')

class CategoriaManager(Manager):
    def get_queryset(self):
        return CategoriaQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset().search(query=query)

    def interna(self):
        return self.get_queryset().interna()

    def externa(self):
        return self.get_queryset().externa()

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
    puntos_volumen = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
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
    
    @property
    def precios_cliente(self):
        qs = self.precioclientepreferente_set.filter(activo=True).first() #type:ignore
        return qs

    def __str__(self):
        return self.nombre
    
    def get_details(self):
        return self.detalles_set.all() #type: ignore

class PrecioDistribuidor(Model):
    categoria = ForeignKey(Categoria, on_delete=CASCADE)
    distribuidor = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    consultor_mayor = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    productor_calificado = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    mayorista = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    activo = BooleanField(default=True)
    inserted_on = DateField(auto_now_add=True)
    edited_on = DateField(auto_now=True)

    
    def __str__(self):
        return str(self.categoria.nombre)

class PrecioClientePreferente(Model):
    categoria = ForeignKey(Categoria, on_delete=CASCADE)
    oro = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    plata = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    bronce = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    cliente = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    activo = BooleanField(default=True)
    inserted_on = DateField(auto_now_add=True)
    edited_on = DateField(auto_now=True)

    def __str__(self):
        return str(self.categoria)
    

class Sabor(Model):

    nombre = CharField(max_length=64)
    descripcion = CharField(max_length=255, blank=True, null=True)
    categoria = ManyToManyField('Categoria', blank=True)

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
    cantidad_decimal = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    unidad = CharField(max_length=50, validators=[validar_unidad_de_medida])

    

    objects = DetallesManager()
    
    def save(self, *args, **kwargs):
        valor = get_decimal_for_save(self.cantidad)
        self.cantidad_decimal, self.unidad = todo_a_gramos(valor, self.unidad)
        self.cantidad = self.cantidad_decimal
        super().save(*args, **kwargs)
    
    class Meta:
        managed = True
        verbose_name = 'Detalle'
        verbose_name_plural = 'Detalles'

    def __str__(self):
        return self.sabor
    
class Porcion(Model):

    categoria = OneToOneField(Categoria, on_delete=CASCADE)    
    precio = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
    cantidad = CharField(max_length=50)
    cantidad_decimal = DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)
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
        costo = round(self.cantidad_decimal * precio / cant_total, 2) #type: ignore
        return costo
    
    def save(self, *args, **kwargs):
        valor = get_decimal_for_save(self.cantidad)
        self.cantidad_decimal, self.unidad = todo_a_gramos(valor, self.unidad)
        self.cantidad = self.cantidad_decimal
        super().save(*args, **kwargs)

 
    def __str__(self):
        return str(self.categoria)
    

class PalabrasClaveQuerySet(QuerySet):
    def search(self, query=None):
        if query is None or query == "":
            return self.none()
        lookups = (
            Q(palabra__icontains=query)
        )
        print(lookups)
        return self.filter(lookups)

class PalabrasClaveManager(Manager):
    def get_queryset(self):
        return PalabrasClaveQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset().search(query=query)

class PalabrasClave(Model):

    palabra = CharField(max_length=32)
    categoria = ManyToManyField(Categoria, blank=True)

    objects = PalabrasClaveManager()

    def __str__(self):
        return str(self.palabra)
