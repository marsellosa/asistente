from django.contrib.auth.models import User
from django.db.models import Sum, DecimalField
from django.shortcuts import get_object_or_404
from consumos.models import Consumo, Transferencia
from prepagos.models import Pago, Prepago
from operadores.models import Operador
from main.utils import get_today
from datetime import datetime, timedelta
from decimal import Decimal

def day_of_year_to_date(year, day_of_year):
    # Crear una fecha que corresponde al primer día del año
    start_of_year = datetime(year, 1, 1)
    # Sumar el número de días menos uno para obtener la fecha correcta
    target_date = start_of_year + timedelta(days=day_of_year - 1)
    return target_date

def get_first_day_of_iso_year(year):
    """Calcula el primer día (lunes) de la primera semana ISO del año."""
    jan4 = datetime(year, 1, 4)  # Enero 4 siempre está en la primera semana ISO
    return jan4 - timedelta(days=jan4.weekday())

def obtener_fecha_inicio_fin_semana(anio, numero_semana):
    """
    Devuelve el rango de fechas para una semana ISO específica.
    
    Args:
        anio (int): Año ISO.
        numero_semana (int): Número de semana ISO (1-53).
    
    Returns:
        tuple: (inicio_semana, fin_semana) como datetime.date.
    """
    primer_dia_iso = get_first_day_of_iso_year(anio)
    inicio_semana = primer_dia_iso + timedelta(weeks=numero_semana - 1)
    fin_semana = inicio_semana + timedelta(days=6)
    return inicio_semana.date(), fin_semana.date()

def obtener_semana_iso(fecha):
    """Devuelve el año y semana ISO de una fecha."""
    if isinstance(fecha, str):
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
    anio_iso, numero_semana, _ = fecha.isocalendar()
    return anio_iso, numero_semana

def obtener_rango_semana_a_partir_de_fecha(fecha):
    """
    Devuelve la semana ISO y su rango de fechas (lunes-domingo).
    
    Args:
        fecha (str o datetime.date): Fecha en formato 'YYYY-MM-DD' o date.
    
    Returns:
        tuple: (numero_semana, inicio_semana, fin_semana).
    """
    anio_iso, numero_semana = obtener_semana_iso(fecha)
    inicio, fin = obtener_fecha_inicio_fin_semana(anio_iso, numero_semana)
    return numero_semana, inicio, fin

def prepagos_list(id_operador=None, activo=True):

    if id_operador is not None:
        prepagos = Prepago.objects.filter(socio__operador__id=id_operador, activo=activo).order_by('-created')
    else:
        prepagos = Prepago.objects.filter(activo=activo).order_by('-created')
        
    acumulado = round(sum([prepago.get_acumulado() for prepago in prepagos]), 2)
    gastado = round(sum([prepago.total_gastado() for prepago in prepagos]), 2)

    ppagos = {
        'lista': prepagos,
        'acumulado' : acumulado,
        'saldo' : round(sum([prepago.get_saldo() for prepago in prepagos]), 2),
        'gastado' : gastado,
        'disponible' : round(acumulado - gastado, 2)
    }
    
    return ppagos

def get_pp_oper(pp_oper):
    # Cálculo para transferencias
    total_transferencias = pp_oper.filter(
        transferenciapp__isnull=False
    ).aggregate(
        total=Sum('monto', output_field=DecimalField())
    )['total'] or Decimal('0')
    total_transferencias = total_transferencias.quantize(Decimal('0.00'))

    # Cálculo para efectivo
    total_efectivo = pp_oper.filter(
        transferenciapp__isnull=True
    ).aggregate(
        total=Sum('monto', output_field=DecimalField())
    )['total'] or Decimal('0')
    total_efectivo = total_efectivo.quantize(Decimal('0.00'))

    return total_efectivo, total_transferencias


def get_cons_oper(consumos):
    # Transferencias (registros con transferencia)
    transferencias = consumos.filter(transferencia__isnull=False)
    total_transferencias = transferencias.aggregate(
        total=Sum('efectivo', output_field=DecimalField())
    )['total'] or Decimal('0')
    total_transferencias = total_transferencias.quantize(Decimal('0.00'))

    # Efectivo (registros sin transferencia)
    efectivo = consumos.filter(transferencia__isnull=True)
    total_efectivo = efectivo.aggregate(
        total=Sum('efectivo', output_field=DecimalField())
    )['total'] or Decimal('0')
    total_efectivo = total_efectivo.quantize(Decimal('0.00'))

    return total_efectivo, total_transferencias

def reporte_consumos(id_operador=None, fechaDesde=None, fechaHasta=None, user=None):
    context, consumos = {}, []
    
    rango = (
        fechaDesde is not None and
        fechaHasta is not None
    )
    
    if fechaDesde is None:
        fechaDesde = get_today()
    
    if rango:
        consumos = Consumo.objects.by_date_range(fechaDesde, fechaHasta)  # type: ignore
        prepagos = Pago.objects.pago_by_date_range(fechaDesde, fechaHasta)
    else:
        consumos = Consumo.objects.by_date(fechaDesde)  # type: ignore
        prepagos = Pago.objects.pago_by_date(fechaDesde)
    
    # Listas para separar usuarios por tipo de pago
    socios_efectivo_consumos = set()
    socios_transferencia_consumos = set()
    socios_efectivo_prepagos = set()
    socios_transferencia_prepagos = set()
    
    if id_operador is not None:
        operador = get_object_or_404(Operador, id=id_operador)
        lista_prepagos = prepagos_list(id_operador=id_operador)
        usuario = operador.licencia.persona.usuario
        try:
            cons_user = consumos.by_user(usuario)
            prep_user = prepagos.by_user(usuario)
        except:
            pass
        consumos = consumos.by_id_operador(id_operador)  # type: ignore
        prepagos = prepagos.filter(prepago__socio__operador=operador)
    else:
        operador = None
        lista_prepagos = prepagos_list()

    
    # Separar usuarios por tipo de pago en consumos
    socios_efectivo_consumos = consumos.filter(transferencia__isnull=True)
    socios_transferencia_consumos = consumos.filter(transferencia__isnull=False)
    total_efectivo_consumos = round(sum([item.efectivo for item in consumos]), 2)
    
    # Separar usuarios por tipo de pago en prepagos
    socios_efectivo_prepagos = prepagos.filter(transferenciapp__isnull=True)
    socios_transferencia_prepagos = prepagos.filter(transferenciapp__isnull=False)
    
    # Calcular totales
    
    pagos = get_cons_oper(consumos)
    ppagos = get_pp_oper(prepagos)
    

    pagos_totales = round(sum(pagos + ppagos), 2)
    total_efectivo = round(sum([pagos[0], ppagos[0]]), 2)
    total_transferencia = round(sum([pagos[1], ppagos[1]]), 2)
    
    # print(f'socios_efectivo_consumos: {list(socios_efectivo_consumos)}')
    # print(f"socios_transferencia_consumos: {list(socios_transferencia_consumos)}")
    # print(f'socios_efectivo_prepagos: {list(socios_efectivo_prepagos)}')
    # print(f"socios_transferencia_prepagos: {list(socios_transferencia_prepagos)}")
    
    # Agregar listas al contexto
    context = {
        'prepagos': lista_prepagos,
        'operador': operador,
        'consumos': consumos,
        'hoy': fechaDesde,
        'nro_sem': obtener_semana_iso(fechaDesde)[1],
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
            'pagos_ef': pagos[0],
            'pagos_qr': pagos[1],
            'ppagos_ef': ppagos[0],
            'ppagos_qr': ppagos[1],
            'total_pagos': pagos_totales,
            'total_efectivo': total_efectivo,
            'total_transferencia': total_transferencia,
        },
        'socios_efectivo_consumos': list(socios_efectivo_consumos),
        'socios_transferencia_consumos': list(socios_transferencia_consumos),
        'socios_efectivo_prepagos': list(socios_efectivo_prepagos),
        'socios_transferencia_prepagos': list(socios_transferencia_prepagos),
    }
    
    return context

def reporte_semanal(fecha=None, id_operador=None):
    """
    Devuelve el número de semana ISO, el lunes y el domingo correspondientes a una fecha dada.
    
    Args:
        fecha (str o datetime.date): Fecha en formato 'YYYY-MM-DD' o como objeto datetime.date/datetime.datetime.
    
    Returns:
        tuple: (número_semana_ISO, fecha_lunes, fecha_domingo) como (int, datetime.date, datetime.date).
    """
    if fecha is None:
        fecha = get_today()
        
    # print(f"fecha: {fecha}")
    # Obtener año ISO y número de semana
    anio_iso, numero_semana = obtener_semana_iso(fecha)
    # print(anio_iso, numero_semana)
    # Obtener fechas de inicio y fin de la semana
    inicio_semana, fin_semana = obtener_fecha_inicio_fin_semana(anio_iso, numero_semana)
    # print(inicio_semana, fin_semana)

    context = reporte_consumos(id_operador=id_operador, fechaDesde=inicio_semana, fechaHasta=fin_semana)
    
    return context