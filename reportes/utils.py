from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from consumos.models import Consumo
from prepagos.models import Pago
from operadores.models import Operador
from main.utils import get_today

def reporte_consumos(id_operador=None, fechaDesde=None, fechaHasta=None, user=None):
    context, consumos = {}, []
    # lista = Consumo.objects.by_id_operador(id_operador) #type: ignore
    if fechaDesde is None:
        fechaDesde = get_today().date()
    # registrados = Consumo.objects.by_user(id_operador, fechaDesde) #type: ignore
    # consumos = lista.filter(comanda__fecha=fechaDesde).order_by('-id')
    # efectivo_prepago = Pago.objects.filter(fecha__date=fechaDesde, usuario__id=id_operador)
    # prepagos_operador  = Pago.objects.filter(fecha__date=fechaDesde, prepago__socio__operador__id=id_operador).order_by('-fecha')
        
    rango = (
        fechaDesde is not None and
        fechaHasta is not None
    )
    
    print(f"id_operador: {type(id_operador)}")
    if rango:
        print(f"con rango: {fechaDesde} hasta: {fechaHasta}")
        consumos = Consumo.objects.filter(comanda__fecha__gte=fechaDesde, comanda__fecha__lte=fechaHasta).order_by('-comanda__fecha')
        efectivo_prepago = Pago.objects.filter(fecha__date__gte=fechaDesde, fecha__date__lte=fechaHasta)
        
    else:
        print(f'sin rango: {fechaDesde}')
        # consumos = Consumo.objects.filter(comanda__fecha=fechaDesde).order_by('-comanda__fecha')
        consumos = Consumo.objects.by_date(fechaDesde) # type: ignore
        
        efectivo_prepago = Pago.objects.filter(fecha__date=fechaDesde)
    # if user is not None:
    #     prepagos_x_usuario = efectivo_prepago.filter(usuario=user)
    #     print(prepagos_x_usuario)
    if type(id_operador) is int:
        # consumos = consumos.filter(comanda__socio__operador__id=id_operador)
        # print(f"usuario: {Operador.objects.get(id=id_operador).licencia.persona.usuario_set.all().first()}")
        consumos = consumos.by_id_operador(id_operador) # type: ignore
        efectivo_prepago = efectivo_prepago.filter(prepago__socio__operador__id=id_operador)
        # efec_prepago_by_operador =efectivo_prepago.filter(prepago__socio__operador__id=id_operador)
    print(consumos)
    # context = {
    #     'consumos': consumos,
    # }
    print(f"total_consumido: {round(sum([item.total_consumido for item in consumos]), 2)}")
    context = {
        'id_operador': id_operador,
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
    #         'prepagos_x_id' : round(sum([item.monto for item in prepagos_operador]) ,2)
        },
    }
    
    return context