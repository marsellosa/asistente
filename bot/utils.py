import random
import string

def generate_pin(length=6):
    upper_limit = 10 ** length
    pin = random.randint(0, upper_limit-1)
    return "{:0{length}d}".format(pin, length=length)

def generar_numero_aleatorio(longitud=6):
    numero = ""
    for _ in range(longitud):
        digito = random.randint(0, 9)
        numero += str(digito)
    return int(numero)

def generar_codigo_alfanumerico(longitud=15):
    caracteres = string.ascii_letters + string.digits
    codigo = ''.join(random.choice(caracteres) for _ in range(longitud))
    return codigo

