from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

from prepagos.models import Pago, Prepago

@receiver(pre_save, sender=Pago)
def set_prepago_payed(instance, **kwargs):
    if instance.monto >= instance.prepago.get_saldo():
        saldo = instance.monto - instance.prepago.get_saldo()
        instance.monto = instance.prepago.get_saldo()
        instance.prepago.pagado = True
        instance.prepago.save()
        if saldo > 0:
            prepago = Prepago.objects.create(
                socio=instance.prepago.socio,
                cantidad = instance.prepago.cantidad,
                descuento = instance.prepago.descuento,
                valor=instance.prepago.valor
            )
            Pago.objects.create(
                usuario=instance.usuario,
                prepago=prepago, 
                monto=saldo
            )

@receiver(post_delete, sender=Pago)
def update_prepago(instance, **kwargs):
    if instance.prepago.get_saldo() > 0:
        instance.prepago.pagado = False
        instance.prepago.save()
