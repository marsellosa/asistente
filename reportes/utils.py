from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from consumos.models import Consumo
from prepagos.models import Pago
from operadores.models import Operador
from main.utils import get_today

def reporte_consumos(id_operador=None, fechaDesde=None, fechaHasta=None, user=None):
    context, consumos = {}, []
    
    if fechaDesde is None:
        fechaDesde = get_today().date()

    prepagos_operador  = Pago.objects.filter(fecha__date=fechaDesde, prepago__socio__operador__id=id_operador).order_by('-fecha')
        
    rango = (
        fechaDesde is not None and
        fechaHasta is not None
    )
    
    if rango:
        consumos = Consumo.objects.by_date_range(fechaDesde, fechaHasta) #type: ignore
        # consumos = Consumo.objects.filter(comanda__fecha__gte=fechaDesde, comanda__fecha__lte=fechaHasta).order_by('-comanda__fecha')
        efectivo_prepago = Pago.objects.filter(fecha__date__gte=fechaDesde, fecha__date__lte=fechaHasta)
    else:
        consumos = Consumo.objects.by_date(fechaDesde) # type: ignore
        efectivo_prepago = Pago.objects.filter(fecha__date=fechaDesde)
    
    if id_operador is not None:
        consumos = consumos.by_id_operador(id_operador) # type: ignore
        efectivo_prepago = efectivo_prepago.filter(prepago__socio__operador__id=id_operador)

    context = {
        'operador': Operador.objects.get(pk=id_operador),
        'consumos': consumos,
        'hoy': fechaDesde,
        'totales': {
            'total': consumos.count(),
            'sobre_rojo': round(sum([item.sobre_rojo for item in consumos]), 2),
            'mayoreo': round(sum([item.mayoreo for item in consumos]), 2),
            'insumos': round(sum([item.insumos for item in consumos]), 2),
            'descuento': round(sum([item.descuento for item in consumos]), 2),
            'puntos_volumen': round(sum([item.puntos_volumen for item in consumos]), 2),
            'sobre_verde': round(sum([item.sobre_verde for item in consumos]), 2),
            'efectivo': round(sum([item.efectivo for item in consumos]), 2),
            'efectivo_prepago': round(sum([item.monto for item in efectivo_prepago]), 2),
            'efectivo_consumos': round(sum([item.efectivo for item in consumos]), 2),
            'prepagos_x_id' : round(sum([item.monto for item in prepagos_operador]) ,2)
        },
    }
    
    return context