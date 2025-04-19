from django.db.models import Sum, Case, When, DecimalField, Value, Count
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from consumos.models import Consumo
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
    inicio_semana, fin_semana = obtener_fecha_inicio_fin_semana(anio_iso, numero_semana)
    return anio_iso, numero_semana, inicio_semana, fin_semana

def prepagos_list(codigo_operador=None, activo=True):
    queryset = Prepago.objects.filter(activo=activo).order_by('-created')
    if codigo_operador:
        queryset = queryset.filter(socio__operador__codigo_operador=codigo_operador)

    acumulado = sum(prepago.get_acumulado() for prepago in queryset)
    # Calcular gastado iterando sobre los objetos (ya que total_gastado es un método)
    gastado = sum(prepago.total_gastado() for prepago in queryset)
    saldo = acumulado - gastado

    return {
        'lista': queryset,
        'acumulado': round(acumulado, 2),
        'saldo': round(saldo, 2),
        'gastado': round(gastado, 2),
        'disponible': round(acumulado - gastado, 2),
    }

def calcular_totales(queryset, campo_monto, campo_filtro):
    """
    Función auxiliar para calcular totales basados en un filtro específico.
    """
    total = queryset.aggregate(
        efectivo_=Sum(
            Case(
                When(**{f"{campo_filtro}__isnull": True}, then=campo_monto),
                default=Value(0),
                output_field=DecimalField(),
            )
        ),
        transferencias=Sum(
            Case(
                When(**{f"{campo_filtro}__isnull": False}, then=campo_monto),
                default=Value(0),
                output_field=DecimalField(),
            )
        ),
    )

    # Redondear los resultados a 2 decimales
    total_efectivo = (total['efectivo_'] or Decimal('0')).quantize(Decimal('0.00'))
    total_transferencias = (total['transferencias'] or Decimal('0')).quantize(Decimal('0.00'))

    return total_efectivo, total_transferencias


def get_pp_oper(pp_oper):
    """
    Calcula los totales de prepagos por tipo de pago (efectivo y transferencia).
    """
    return calcular_totales(pp_oper, 'monto', 'transferenciapp')


def get_cons_oper(consumos):
    """
    Calcula los totales de consumos por tipo de pago (efectivo y transferencia).
    """
    return calcular_totales(consumos, 'efectivo', 'transferencia')

def reporte_consumos_diario(codigo_operador=None, fechaDesde=None, fechaHasta=None, user=None):
    context = {}
    
    # Manejo de fechas
    if fechaDesde is None:
        fechaDesde = get_today().strftime('%Y-%m-%d')
    
    rango = fechaDesde and fechaHasta  # Determina si se trabaja con un rango o una sola fecha
    
    # Filtrar consumos y prepagos según el rango de fechas
    consumos = (
        Consumo.objects.by_date_range(fechaDesde, fechaHasta) if rango
        else Consumo.objects.by_date(fechaDesde)
    )
    prepagos = (
        Pago.objects.pago_by_date_range(fechaDesde, fechaHasta) if rango
        else Pago.objects.pago_by_date(fechaDesde)
    )
    
    # Filtrar por operador si se proporciona el código
    if codigo_operador:
        operador = get_object_or_404(Operador, codigo_operador=codigo_operador)
        # usuario = operador.licencia.persona.usuario
        consumos = consumos.by_operador(operador=operador)
        prepagos = prepagos.filter(prepago__socio__operador=operador)
    else:
        operador = None
    
    # Separar usuarios por tipo de pago (en consumos y prepagos)
    socios_efectivo_consumos = consumos.filter(transferencia__isnull=True)
    socios_transferencia_consumos = consumos.filter(transferencia__isnull=False)
    socios_efectivo_prepagos = prepagos.filter(transferenciapp__isnull=True)
    socios_transferencia_prepagos = prepagos.filter(transferenciapp__isnull=False)
    
    # Agregar valores predeterminados a las sumas y contar
    totales_consumos = consumos.aggregate(
        total=Count('id'),
        sobre_rojo=Coalesce(Sum('sobre_rojo'), Value(0), output_field=DecimalField()),
        mayoreo=Coalesce(Sum('mayoreo'), Value(0), output_field=DecimalField()),
        insumos=Coalesce(Sum('insumos'), Value(0), output_field=DecimalField()),
        descuento=Coalesce(Sum('descuento'), Value(0), output_field=DecimalField()),
        puntos_volumen=Coalesce(Sum('puntos_volumen'), Value(0), output_field=DecimalField()),
        sobre_verde=Coalesce(Sum('sobre_verde'), Value(0), output_field=DecimalField()),
        efectivo=Coalesce(Sum('efectivo'), Value(0), output_field=DecimalField()),
    )

    totales_prepagos = prepagos.aggregate(
        pp_oper=Coalesce(Sum('monto'), Value(0), output_field=DecimalField()),
    )

    # Redondear valores numéricos y convertirlos a Decimal
    for key, value in totales_consumos.items():
        if isinstance(value, (int, float, Decimal)):
            totales_consumos[key] = Decimal(value).quantize(Decimal('0.00'))
    
    if totales_prepagos['pp_oper'] is not None:
        totales_prepagos['pp_oper'] = round(totales_prepagos['pp_oper'], 2)
    
    # Calcular pagos totales (efectivo y transferencia)
    pagos_efectivo = sum([
        socios_efectivo_consumos.aggregate(total=Sum('efectivo'))['total'] or 0,
        socios_efectivo_prepagos.aggregate(total=Sum('monto'))['total'] or 0
    ])
    
    pagos_transferencia = sum([
        socios_transferencia_consumos.aggregate(total=Sum('efectivo'))['total'] or 0,
        socios_transferencia_prepagos.aggregate(total=Sum('monto'))['total'] or 0
    ])
    
    total_pagos = round(pagos_efectivo + pagos_transferencia, 2)
    # print(f"pagos_efectivo: {pagos_efectivo}, pagos_transferencia: {pagos_transferencia} total_pagos: {total_pagos}")
    # Calcular pagos totales (efectivo y transferencia)
    pagos = calcular_totales(consumos, 'efectivo', 'transferencia')
    ppagos = calcular_totales(prepagos, 'monto', 'transferenciapp')
    
    # Construir el contexto
    context = {
        'prepagos': prepagos_list(codigo_operador=codigo_operador),
        'operador': operador,
        'consumos': consumos,
        'hoy': f"{fechaDesde}/{fechaHasta}" if rango else f"{fechaDesde}",
        'nro_sem': obtener_semana_iso(fechaDesde)[1],
        'totales': {
            **totales_consumos,
            **totales_prepagos,
            'pagos_ef': pagos[0],
            'pagos_qr': pagos[1],
            'ppagos_ef': ppagos[0],
            'ppagos_qr': ppagos[1],
            'total_pagos': total_pagos,
            'total_efectivo': pagos_efectivo,
            'total_transferencia': pagos_transferencia,
        },
        'socios_efectivo_consumos': list(socios_efectivo_consumos),
        'socios_transferencia_consumos': list(socios_transferencia_consumos),
        'socios_efectivo_prepagos': list(socios_efectivo_prepagos),
        'socios_transferencia_prepagos': list(socios_transferencia_prepagos),
    }
    
    return context

def reporte_semanal(fecha=None, codigo_operador=None):
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

    context = reporte_consumos_diario(codigo_operador=codigo_operador, fechaDesde=inicio_semana, fechaHasta=fin_semana)
    
    return context