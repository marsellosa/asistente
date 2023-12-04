from django.contrib.auth.models import User
from django.db.models import * #type:ignore
from django.urls import reverse
from django.utils.timezone import now

class PersonaGenero(TextChoices):

    HOMBRE  = 'H', 'Hombre'
    MUJER   = 'M', 'Mujer'

class PersonaQuerySet(QuerySet):
    def search(self, query=None):
        if query is None or query == "":
            return self.none()
        lookups = (
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query)
        )
        # print(lookups)
        return self.filter(lookups)

    def mujeres(self):
        return self.filter(genero=PersonaGenero.MUJER)

    def hombres(self):
        return self.filter(genero=PersonaGenero.HOMBRE)

class PersonaManager(Manager):
    def get_queryset(self):
        return PersonaQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset().search(query=query)

class Persona(Model):
    
    usuario = ForeignKey(User, on_delete=CASCADE, null=True, blank=True)
    nombre = CharField(max_length=32)
    apellido = CharField(max_length=32)
    genero = CharField(max_length=1, choices=PersonaGenero.choices, default=PersonaGenero.MUJER)
    fecha_nacimiento = DateField(default=now)
    activo = BooleanField(default=True)
    profile_pic = ImageField(null=True, blank=True)
    created_on = DateTimeField(auto_now_add=True)
    edited_on = DateTimeField(auto_now=True)

    objects = PersonaManager()

    def get_absolute_url(self):
        return reverse("socios:profile", kwargs={"id": self.pk})

    def get_nivel_licencia(self):
        status = {
            'my': 'Mayorista',
            'pc': 'Productor Calificado',
            'ce': 'Constructor del Exito',
            'cm': 'Consultor Mayor',
            'ds': 'Distribuidor',
            'au': 'Oro',
            'ag': 'Plata',
            'ae': 'Bronce',
            'cl': 'Cliente',
        }
        try:
            nivel = status[str(self.licencia_set.first().status)] #type:ignore
        except:
            nivel = None
        return nivel
    
    def get_bot_id(self):
        try:
            bot_id = self.botuser.user_id #type: ignore
        except:
            bot_id = None
        return bot_id
    
    def get_profile_pic_url(self):
        if self.genero == 'M':
            profile_pic = '/AdminLTE/dist/img/avatar3.png'
        else:
            profile_pic = '/AdminLTE/dist/img/avatar04.png'
        return profile_pic

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Contacto(Model):

    persona = ForeignKey(Persona, verbose_name="id_socio", on_delete=CASCADE)
    dato = CharField(max_length=128)
    tipo = CharField(max_length=128)

    def __str__(self):
        return self.dato
    

class LicenciaStatus(TextChoices):

    MAYORISTA       = 'my', 'Mayorista'
    PRODUCTOR       = 'pc', 'Productor Calificado'
    CONSTRUCTOR     = 'ce', 'Constructor del Exito'
    CONSULTOR       = 'cm', 'Consultor Mayor'
    DISTRIBUIDOR    = 'ds', 'Distribuidor'
    ORO             = 'au', 'Oro'
    PLATA           = 'ag', 'Plata'
    BRONCE          = 'ae', 'Bronce'
    CLIENTE         = 'cl', 'Cliente'

class LicenciaQuerySet(QuerySet):

    def mayorista(self):
        return self.filter(status=LicenciaStatus.MAYORISTA)
        
    def productor(self):
        return self.filter(status=LicenciaStatus.PRODUCTOR)

    def constructor(self):
        return self.filter(status=LicenciaStatus.CONSTRUCTOR)

    def consultor(self):
        return self.filter(status=LicenciaStatus.CONSULTOR)

    def distribuidor(self):
        return self.filter(status=LicenciaStatus.DISTRIBUIDOR)
    
    def oro(self):
        return self.filter(status=LicenciaStatus.ORO)
        
    def plata(self):
        return self.filter(status=LicenciaStatus.PLATA)
        
    def bronce(self):
        return self.filter(status=LicenciaStatus.BRONCE)
        
    def cliente(self):
        return self.filter(status=LicenciaStatus.CLIENTE)

class LicenciaManager(Manager):
    def get_queryset(self):
        return LicenciaQuerySet(self.model, using=self._db)

class Licencia(Model):

    persona = OneToOneField(Persona, on_delete=CASCADE, blank=True, null=True)
    id_licencia = CharField(max_length=32, blank=True, null=True)
    status = CharField(max_length=2, choices=LicenciaStatus.choices, default=LicenciaStatus.MAYORISTA)

    objects = LicenciaManager()

    def __str__(self):
        return str(self.persona)
