from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from consumos.models import Consumo, Transferencia
from prepagos.models import Pago, Prepago
from operadores.models import Operador
from main.utils import get_today
from datetime import datetime, timedelta

def day_of_year_to_date(year, day_of_year):
    # Crear una fecha que corresponde al primer día del año
    start_of_year = datetime(year, 1, 1)
    # Sumar el número de días menos uno para obtener la fecha correcta
    target_date = start_of_year + timedelta(days=day_of_year - 1)
    return target_date

def prepagos_list(id_operador=None, activo=True):

    if id_operador is not None:
        prepagos = Prepago.objects.filter(socio__operador__id=id_operador, activo=activo)
    else:
        prepagos = Prepago.objects.filter(activo=activo)
    
    return prepagos.order_by('-created')

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
        
        prepagos = Pago.objects.pago_by_date_range(fechaDesde, fechaHasta)
    else:
        consumos = Consumo.objects.by_date(fechaDesde) # type: ignore
        
        # con_trans = consumos.filter(transferencia__isnull=False)
        prepagos = Pago.objects.pago_by_date(fechaDesde)
    
    if id_operador is not None:
        operador = get_object_or_404(Operador, id=id_operador)
        lista_prepagos = prepagos_list(id_operador=id_operador)
        usuario = operador.licencia.persona.usuario
        try:
            cons_user = consumos.by_user(usuario)
            prep_user = prepagos.by_user(usuario)
            # print(f"fecha: {fechaDesde}, ef_cons_user, qr_cons_user: {get_cons_oper(cons_user)}")
            # print(f"fecha: {fechaDesde}, ef_prep_user, qr_prep_user: {get_pp_oper(prep_user)}")
        except:
            pass
        consumos = consumos.by_id_operador(id_operador) # type: ignore
        prepagos = prepagos.filter(prepago__socio__operador=operador)
        # print(f"pp_oper: {pp_oper}")
    else:
        operador = None
        lista_prepagos = prepagos_list()

    acumulado = round(sum([prepago.get_acumulado() for prepago in lista_prepagos]), 2)
    saldo = round(sum([prepago.get_saldo() for prepago in lista_prepagos]), 2)
    gastado = round(sum([prepago.total_gastado() for prepago in lista_prepagos]), 2)
    disponible = round(acumulado - gastado, 2)
    pagos = get_cons_oper(consumos)
    ppagos = get_pp_oper(prepagos)
    pagos_totales = sum(pagos + ppagos)

    context = {
        'ppagos' : {
            'acumulado' : acumulado,
            'saldo' : saldo,
            'gastado' : gastado,
            'disponible' : disponible
        },
        'prepagos' : lista_prepagos,
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
            'pp_oper': round(sum([item.monto for item in prepagos]), 2),
            'efectivo_consumos': round(sum([item.efectivo for item in consumos]), 2),
            'pagos_ef': pagos[0],
            'pagos_qr': pagos[1],
            'ppagos_ef': ppagos[0],
            'ppagos_qr': ppagos[1],
            'total_pagos': pagos_totales,
        },
    }
    
    return context

