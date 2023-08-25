from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from consumos.models import Consumo
from comanda.models import Comanda, ComandaItem


@receiver(post_save, sender=Comanda)
def create_consumo(sender, instance, created, **kwargs):
    if created:
        Consumo.objects.create(comanda=instance)
    else:
        update_consumo(instance)

@receiver(post_save, sender=ComandaItem)
def create_comanda_item(sender, instance, created, **kwargs):
    update_consumo(instance.comanda)

@receiver(post_delete, sender=ComandaItem)
def delete_comanda_item(sender, instance, **kwargs):
    update_consumo(instance.comanda)

def update_consumo(instance):
    # ins = instance.comanda
    Consumo.objects.update_or_create(
        comanda = instance,
        defaults={
            'total_consumido' : instance.get_cart_total,
            'sobre_rojo' : instance.get_sobre_rojo,
            'mayoreo': instance.get_mantenimiento,
            'puntos_volumen': instance.get_cart_points,
            'insumos': instance.get_insumos,
            'descuento': instance.get_total_descuento,
            'sobre_verde': instance.get_sobre_verde,
            'efectivo': instance.get_cart_cash,
        }
    )

    
