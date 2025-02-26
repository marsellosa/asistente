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

def obtener_fecha_inicio_fin_semana(anio, numero_semana):
    """
    Devuelve la fecha del primer y último día de una semana específica en un año dado,
    asegurándose de que el número de semana sea válido.
    
    Args:
        numero_semana (int): Número de la semana (1-53).
        anio (int): Año al que pertenece la semana.
    
    Returns:
        tuple: Fecha del primer día (lunes) y del último día (domingo) en formato datetime.date.
    
    Raises:
        ValueError: Si el número de semana no es válido para el año dado.
    """
    # Validar el número máximo de semanas en el año ISO
    ultimo_dia_anio = datetime(anio, 12, 31)
    
    # Aseguramos que el último día pertenece al año actual y calculamos semanas
    if ultimo_dia_anio.isocalendar()[0] != anio:
        # Si el último día no pertenece al año ISO actual, retrocedemos para calcular el límite correcto
        ultimo_dia_anio -= timedelta(days=ultimo_dia_anio.weekday() + 1)
    semanas_en_anio = ultimo_dia_anio.isocalendar()[1]
    
    if numero_semana < 1 or numero_semana > semanas_en_anio:
        raise ValueError(f"El número de semana {numero_semana} no es válido para el año {anio}. "
                         f"Debe estar entre 1 y {semanas_en_anio}.")
    
    # Calcula el primer día del año
    primer_dia_anio = datetime(anio, 1, 1)
    
    # Encuentra el primer lunes del año (semana ISO inicia en lunes)
    primer_lunes = primer_dia_anio + timedelta(days=(7 - primer_dia_anio.weekday()) % 7)
    
    # Calcula el inicio de la semana deseada
    inicio_semana = primer_lunes + timedelta(weeks=numero_semana - 1)
    
    # Verifica que el inicio de la semana no exceda el año
    if inicio_semana.year != anio:
        raise ValueError(f"La semana {numero_semana} no corresponde al año {anio}.")
    
    # Fin de la semana (domingo)
    fin_semana = inicio_semana + timedelta(days=6)
    
    return inicio_semana.date(), fin_semana.date()


def obtener_semana_iso(fecha):
    """
    Devuelve el año y número de semana ISO de una fecha dada.
    
    Args:
        fecha (str): Fecha en formato 'YYYY-MM-DD'.
    
    Returns:
        tuple: Año ISO y número de semana ISO.
    """
    # Convertir la fecha a objeto datetime
    if isinstance(fecha, str):
        # Convierte la fecha de string a datetime
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
    
    # Obtener el año ISO y el número de semana
    anio_iso, numero_semana, _ = fecha.isocalendar()
    
    return anio_iso, numero_semana

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
    # print(f"efectivo: {list(efectivo)}, transferencias: {transferencias}")
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
    
    # Separar usuarios por tipo de pago en prepagos
    socios_efectivo_prepagos = prepagos.filter(transferenciapp__isnull=True)
    socios_transferencia_prepagos = prepagos.filter(transferenciapp__isnull=False)
    
    # Calcular totales
    pagos = get_cons_oper(consumos)
    ppagos = get_pp_oper(prepagos)
    pagos_totales = round(sum(pagos + ppagos), 2)

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
        },
        'socios_efectivo_consumos': list(socios_efectivo_consumos),
        'socios_transferencia_consumos': list(socios_transferencia_consumos),
        'socios_efectivo_prepagos': list(socios_efectivo_prepagos),
        'socios_transferencia_prepagos': list(socios_transferencia_prepagos),
    }
    
    return context

