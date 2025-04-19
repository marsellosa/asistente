from django.db.models import * # type: ignore

class Semana(Model):
    anio = IntegerField()
    numero_semana = IntegerField()
    inicio_semana = DateField()
    fin_semana = DateField()

    def __str__(self):
        return f"Semana {self.numero_semana} del año {self.anio}"
    


