from django.db.models.signals import post_save, pre_save, post_delete
from django.db import transaction
from decimal import Decimal
from django.dispatch import receiver
from prepagos.models import Pago, Prepago

@receiver(pre_save, sender=Pago)
def set_prepago_payed(instance, **kwargs):
    # Evitar recursión si el pago es generado por este mismo signal
    if hasattr(instance, '_handling_prepago'):
        return

    prepago = instance.prepago
    if not prepago:
        return

    with transaction.atomic():
        # Refrescar datos desde la base para evitar condiciones de carrera
        prepago.refresh_from_db()
        saldo_actual = prepago.get_saldo()

        if instance.monto >= saldo_actual:
            # Calcular excedente con precisión decimal
            excedente = instance.monto - saldo_actual
            instance.monto = saldo_actual
            
            # Marcar como pagado y guardar con transacción
            prepago.pagado = True
            prepago.save()

            # Crear nuevo prepago y pago solo si hay excedente
            if excedente > Decimal('0'):
                nuevo_prepago = Prepago.objects.create(
                    socio=prepago.socio,
                    cantidad=prepago.cantidad,
                    descuento=prepago.descuento,
                    valor=prepago.valor
                )

                # Crear nuevo pago con bandera para evitar recursión
                nuevo_pago = Pago(
                    usuario=instance.usuario,
                    prepago=nuevo_prepago,
                    monto=excedente
                )
                nuevo_pago._handling_prepago = True
                nuevo_pago.save()



@receiver(post_delete, sender=Pago)
def update_prepago(instance, **kwargs):
    if instance.prepago.get_saldo() > 0:
        instance.prepago.pagado = False
        instance.prepago.save()
