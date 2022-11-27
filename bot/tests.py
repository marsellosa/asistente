from django.test import TestCase
from bot.views import send_m_bot
from django.db.models import Q
from productos.models import Categoria, Detalles

# send_m_bot(779630771, 'Hola Marcelo!')

def response_msg(producto):
    msg = None
    # print(f"producto.detalle: {producto.detalle}")
    try:
        msg = str(producto.detalle).format(
            producto.descripcion, 
            producto.cantidad, 
            producto.puntos_volumen, 
            producto.precios_distribuidor.distribuidor, 
            producto.precios_distribuidor.consultor_mayor, 
            producto.precios_distribuidor.productor_calificado, 
            producto.precios_distribuidor.mayorista,
            )
    except:
        msg = "No hay Datos"
    return msg

def buscar_x_detalles(text):
    prods = Detalles.objects.search(query=text)
    try:
        productos = [prod.categoria for prod in prods]
    except:
        productos = None

    return productos

text = 'vainilla'
    # calcula y envia el precio del producto solicitado
    # dolar = Settings.objects.get(nombre='Dolar')
msg, link, image = None, None, None


# Procesamos la respuesta al usurio
# TODO corregir el codigo de msg para limpiar codigo
try:
    producto = Categoria.objects.get(nombre__iexact=text, activo=True)
    image = producto.image_url
    msg = response_msg(producto)
    print(f"msg: {msg}")
except:
    productos = []
    print("Buscando por otras caracteristicas")
    # productos = Categoria.objects.filter(
    #     Q(nombre__icontains=text) |
    #     Q(descripcion__icontains=text) |
    #     Q(palabras_clave__icontains=text),
    #     activo=True
    # )
    productos = Categoria.objects.search(query=text)
    if not productos or productos is None:
        print("Buscando por detalles")
        productos = buscar_x_detalles(text)

    print(f"productos: {productos}")

    if len(productos) == 1:
        producto = productos[0]
        msg = response_msg(producto)
        # image = producto.image_url

    elif len(productos) > 1:
        msg = "Tal vez buscas:\n"
        # link = InlineKeyboardMarkup()
        
        # for producto in productos:
        #     link.add(InlineKeyboardButton(text=str(producto), callback_data=str(producto)))
    else:
        # escoge un mensaje aleatorio
        msg = 'mensaje Aleatorio'
    print(f"msg: {msg}")