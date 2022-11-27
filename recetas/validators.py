import pint
from django.core.exceptions import ValidationError
from pint.errors import UndefinedUnitError

def validar_unidad_de_medida(value):
    ureg = pint.UnitRegistry()
    try:
        single_unit = ureg[value]
    except UndefinedUnitError as e:
        raise ValidationError(f'"{value}" no es una unidad de medida válida')
    