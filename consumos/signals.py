from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
from .models import Consumo
from finanzas.models import Movimiento, MovimientoTipo, SobreTipo
from reportes.models import Semana  # Asegúrate de importar correctamente los modelos
from reportes.utils import obtener_rango_semana_a_partir_de_fecha, reporte_consumos_diario


@receiver(post_save, sender=Consumo)
def actualizar_movimientos_al_crear_consumo(sender, created, instance, **kwargs):
    """
    Actualiza los movimientos cuando se crea o modifica un Consumo.
    """
    if not created:
        semana_actual, categorias = obtener_categorias_por_semana(instance)
        
        for tipo_sobre, monto in categorias.items():
                Movimiento.objects.update_or_create(
                    operador = instance.comanda.socio.operador,
                    semana=semana_actual,
                    tipo_sobre=tipo_sobre,
                    defaults={
                        'monto': monto,
                        'tipo_movimiento': MovimientoTipo.INGRESO, 
                        'usuario': instance.comanda.usuario,
                        }
                )


# @receiver(post_delete, sender=Consumo)
# def actualizar_movimientos_al_eliminar_consumo(sender, instance, **kwargs):
#     """
#     Actualiza los movimientos cuando se elimina un Consumo.
#     """
#     try:
#         semana_actual, categorias = obtener_categorias_por_semana(instance)
        
#         for tipo_ingreso, monto in categorias.items():
#             ingreso, creado = Ingreso.objects.update_or_create(
#                 operador = instance.comanda.socio.operador,
#                 semana=semana_actual,
#                 tipo_ingreso=tipo_ingreso,
#                 defaults={
#                     'monto': Decimal('0.00'),
                    
#                 }
#             )

#             if ingreso:
#                 ingreso.monto -= monto
#                 # Evitar montos negativos
#                 ingreso.monto = max(ingreso.monto, Decimal('0.00'))
#                 ingreso.save()
#     except Exception as e:
#         print(f"Error al eliminar movimientos: {e}")
#         # Aquí puedes manejar el error como desees, por ejemplo, registrar en un log


def obtener_categorias_por_semana(instance):
    """
    Calcula los montos de cada categoría en función de la semana correspondiente.
    """
    operador = instance.comanda.socio.operador
    fecha_consumo = instance.comanda.fecha
    anio, numero_semana, inicio_semana, fin_semana = obtener_rango_semana_a_partir_de_fecha(fecha_consumo)
    semana_actual, creado = Semana.objects.get_or_create(
        anio=anio,
        numero_semana=numero_semana,
        defaults={
            'inicio_semana': inicio_semana,
            'fin_semana': fin_semana
        }
    )
    context = reporte_consumos_diario(
        codigo_operador=operador.codigo_operador,
        fechaDesde=inicio_semana,
        fechaHasta=fin_semana,
        user=instance.comanda.usuario
    )
    # print(f"context: {context}")
    # Obtener los montos de cada categoría
    categorias = {
        SobreTipo.SOBREROJO: context['totales']['sobre_rojo'] or Decimal('0.00'),
        SobreTipo.SOBREVERDE: context['totales']['sobre_verde'] or Decimal('0.00'),
        SobreTipo.INSUMOS: context['totales']['insumos'] or Decimal('0.00'),
        SobreTipo.MANTENIMIENTO: context['totales']['mayoreo'] or Decimal('0.00'),
    }
    # print(semana_actual, categorias)
    return semana_actual, categorias