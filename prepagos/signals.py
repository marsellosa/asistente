from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from prepagos.models import Pago, Prepago

@receiver(pre_save, sender=Pago)
def set_prepago_payed(instance, **kwargs):
    print(f"{instance.prepago.get_saldo()}")
    print(f"{instance.monto}")
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
