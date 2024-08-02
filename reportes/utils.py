from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from consumos.models import Consumo, Transferencia
from prepagos.models import Pago
from operadores.models import Operador
from main.utils import get_today, get_aware_date
from datetime import datetime, timedelta

def day_of_year_to_date(year, day_of_year):
    # Crear una fecha que corresponde al primer día del año
    start_of_year = datetime(year, 1, 1)
    # Sumar el número de días menos uno para obtener la fecha correcta
    target_date = start_of_year + timedelta(days=day_of_year - 1)
    return target_date

def get_pp_oper(pp_oper):
    transferencias = pp_oper.filter(transferenciapp__isnull=False)
    efectivo = pp_oper.filter(transferenciapp__isnull=True)
    qr_resultado = transferencias.aggregate(total_efectivo=Sum('monto'))
    ef_resultado = efectivo.aggregate(total_efectivo=Sum('monto'))
    ef_pp_oper = round(ef_resultado['total_efectivo'], 2) if ef_resultado['total_efectivo'] is not None else 0.0
    qr_pp_oper = round(qr_resultado['total_efectivo'], 2) if qr_resultado['total_efectivo'] is not None else 0.0
    return ef_pp_oper, qr_pp_oper



def get_cons_oper(consumos):
    transferencias = consumos.filter(transferencia__isnull=False)
    efectivo = consumos.filter(transferencia__isnull=True)
    # print(f"consumos: {consumos}, transferencias: {transferencias}")
    qr_resultado = transferencias.aggregate(total_efectivo=Sum('efectivo'))
    ef_resultado = efectivo.aggregate(total_efectivo=Sum('efectivo'))
    # ef_cons_oper = round(sum([consumo.efectivo for consumo in consumos]), 2)
    ef_cons_oper = round(ef_resultado['total_efectivo'], 2) if ef_resultado['total_efectivo'] is not None else 0.0
    qr_cons_oper = round(qr_resultado['total_efectivo'], 2) if qr_resultado['total_efectivo'] is not None else 0.0

    return ef_cons_oper, qr_cons_oper

def reporte_consumos(id_operador=None, fechaDesde=None, fechaHasta=None, user=None):
    context, consumos = {}, []
        
    rango = (
        fechaDesde is not None and
        fechaHasta is not None
    )
    
    if fechaDesde is None:
        fechaDesde = get_today()
    
    if rango:
        consumos = Consumo.objects.by_date_range(fechaDesde, fechaHasta) #type: ignore
        pagos = Pago.objects.pago_by_date_range(fechaDesde, fechaHasta)
        pp_oper = Pago.objects.pago_by_date_range(fechaDesde, fechaHasta)
    else:
        consumos = Consumo.objects.by_date(fechaDesde) # type: ignore
        # qr_cons = Transferencia.objects.filter(consumo__comanda__fecha=fechaDesde)
        # con_trans = consumos.filter(transferencia__isnull=False)
        pp_oper = Pago.objects.pago_by_date(fechaDesde)
    
    if id_operador is not None:
        operador = get_object_or_404(Operador, id=id_operador)
        usuario = operador.licencia.persona.usuario
        consumos = consumos.by_id_operador(id_operador) # type: ignore
        pp_oper = pp_oper.filter(prepago__socio__operador=operador)
    else:
        operador = None

    # print(f"user: {user}, operador: {operador}, usuario: {usuario}")
    # print(f"fecha: {fechaDesde}, ef_cons_oper, qr_cons_oper: {get_cons_oper(consumos)}")
    # print(f"fecha: {fechaDesde}, efectivo_pp, transferencias_pp: {get_pp_oper(pp_oper)}")

    context = {
        'operador': operador,
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
            'pp_oper': round(sum([item.monto for item in pp_oper]), 2),
            'efectivo_consumos': round(sum([item.efectivo for item in consumos]), 2),
            # 'prepagos_x_id' : round(sum([item.monto for item in prepagos_operador]) ,2)
        },
    }
    
    return context