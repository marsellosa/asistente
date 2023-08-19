from random import randint

def generate_pin(length=6):
    upper_limit = 10 ** length
    pin = randint(0, upper_limit-1)
    return "{:0{length}d}".format(pin, length=length)

def generar_numero_aleatorio(longitud=6):
    numero = ""
    for _ in range(longitud):
        digito = randint(0, 9)
        numero += str(digito)
    return int(numero)