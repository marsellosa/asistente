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
    """
    Se ejecuta después de eliminar un ComandaItem.
    Actualiza el consumo asociado a la comanda y limpia los prepagos si no quedan items.
    """
    try:
        # Obtener la comanda asociada al item eliminado
        comanda = instance.comanda

        # Verificar si la comanda tiene items restantes
        if not comanda.get_all_items().exists():
            # Obtener los prepagos asociados a la comanda
            prepagos = comanda.get_cart_prepagos

            # Remover todos los prepagos asociados a la comanda
            if prepagos.exists():
                comanda.prepago.clear()

        # Actualizar el consumo asociado a la comanda
        update_consumo(comanda)

    except Exception as e:
        # Registrar cualquier error inesperado
        print(f"Error al procesar la eliminación de ComandaItem: {e}")

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

    
