import pint
from django.core.exceptions import ValidationError
from pint.errors import UndefinedUnitError

def validar_unidad_de_medida(value):
    ureg = pint.UnitRegistry()
    try:
        single_unit = ureg[value]
    except UndefinedUnitError as e:
        raise ValidationError(f'"{value}" no es una unidad de medida válida')
    

def todo_a_gramos(valor, unidad):
    
    ureg = pint.UnitRegistry()
    if valor is not None:
        value = valor * ureg(unidad)
        if value.dimensionality == '[mass]':
            if unidad != 'gr':
                # valor = float(f"{value.to('gram').magnitude:.2f}")
                valor = value.to('gram').magnitude
            unidad = 'gram'
    else:
        valor = 0
    return valor, unidad

    
    

