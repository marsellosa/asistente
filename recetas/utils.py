from decimal import Decimal, InvalidOperation,ROUND_HALF_UP
from fractions import Fraction

def number_str_to_decimal(amount_str: str):
    """
    Convierte una cadena que representa un número o una suma de fracciones en un Decimal redondeado a dos decimales.
    
    Args:
        amount_str (str): La cadena a convertir.
        
    Returns:
        tuple: Un Decimal redondeado a dos decimales (si la conversión fue exitosa) y un indicador de éxito (bool).
    """
    if not isinstance(amount_str, str):
        return None, False  # Retorna None y False si no es una cadena
    
    try:
        # Divide la cadena por espacios y convierte cada parte en una fracción
        total = sum(Fraction(s) for s in amount_str.split())
        number_as_decimal = Decimal(total.numerator) / Decimal(total.denominator)
        
        # Redondea el resultado a dos decimales
        rounded_decimal = number_as_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return rounded_decimal, True
    except (ValueError, ZeroDivisionError, InvalidOperation):
        # Captura errores específicos relacionados con la conversión
        return None, False


def get_decimal_for_save(cant):
    """
    Intenta convertir una cadena en un Decimal redondeado a dos decimales y devuelve el resultado.
    
    Args:
        cant: La entrada a convertir (cadena o número).
        
    Returns:
        Decimal or None: El número Decimal redondeado a dos decimales o None si la conversión falla.
    """
    if isinstance(cant, (int, float)):
        # Si ya es un número, conviértelo directamente a Decimal y redondea a dos decimales
        decimal_value = Decimal(cant).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return decimal_value
    
    cant_decimal, cant_decimal_success = number_str_to_decimal(cant)
    return cant_decimal if cant_decimal_success else None


def get_final_price(costo, margen=50):
    price = costo / (100 - margen) * 100
    return round(price, 2)