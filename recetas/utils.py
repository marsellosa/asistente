from fractions import Fraction

def number_str_to_float(amount_str:str):

    success = False
    number_as_float = amount_str
    try:
        number_as_float = float(sum(Fraction(s) for s in f"{amount_str}".split()))
    except:
        pass
    if isinstance(number_as_float, float):
        success = True
    return number_as_float, success

def get_float_for_save(cant):
    cant_decimal, cant_decimal_success = number_str_to_float(cant)
    if cant_decimal_success:
        return cant_decimal
    else:
        return None
    
def get_final_price(costo, margen=50):
    price = costo / (100 - margen) * 100
    return round(price, 2)