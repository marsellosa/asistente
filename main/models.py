from django.db.models import *


class Settings(Model):

    nombre = CharField("Nombre", max_length=50)
    descripcion = CharField(
        "Descripcion", max_length=100, blank=True, null=True)
    valor = CharField("Valor", max_length=50)

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"

    def __str__(self):
        return self.valor

class Monto(Model):

    monto = IntegerField()
    inserted_on = DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Monto'
        verbose_name_plural = 'Montos'

    def __str__(self):
        return str(self.monto)
