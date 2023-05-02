from time import sleep
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.db.models import Q
from decouple import config
from rest_framework.response import Response
from rest_framework.views import APIView
from bot.forms import MessageForm
from .models import User, Activity
from .chat import respond, welcome
from productos.models import Categoria, Detalles
from main.models import Settings
from pedidos.models import Pedido
import json

import telebot

from telebot.types import InlineKeyboardButton, BotCommand, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup

bot = telebot.TeleBot(config('TOKEN')) #type: ignore


class UpdateBot(APIView):
    def post(self, request):
        json_string = request.body.decode("UTF-8")
        update = telebot.types.Update.de_json(json_string)
        comandos = [BotCommand('hmp', 'Kit de Registro'), BotCommand('interna', 'Nutrición Interna'), BotCommand('externa', 'Nutrición Externa')]
        bot.process_new_updates([update])
        bot.set_my_commands(comandos)
        return Response({'code': 200})


def save_new_user(message):

    from_user = message.from_user
    admin_id = 779630771
    # json_dict = bot.get_user_profile_photos(from_user.id)
    # print(json_dict.photos)
    # [[print(bot.get_file_url(y.file_id)) for y in x] for x in json_dict.photos]
    
    obj, created = User.objects.update_or_create(
        user_id = from_user.id,
        defaults = {
            'first_name': from_user.first_name,
            'last_name': from_user.last_name,
            'username': from_user.username,
            'is_bot': from_user.is_bot,
            'language_code': from_user.language_code,
        }
    )
    if created:
        new_user = f"{obj}, empezó a usar el bot"
        bot.send_message(admin_id, text=new_user)

    return (obj, created)

@bot.message_handler(commands=['sam_cam'])
def sam_cam(message):
    file_dir = 'https://www.estoesherbalife.com/media/kit_files/KitRegistro_07132020.pdf'
    bot.send_document(message.from_user.id, data=file_dir)


# @bot.message_handler(commands=['hmp'])
# def hmp(message):
#     url = 'https://assets.herbalifenutrition.com/content/dam/regional/samcam/es_bo/consumable_content/product-catalog-assets/images/2021/01-Jan/5451.png/_jcr_content/renditions/cq5dam.web.800.800.png'
#     caption = 'Kit de registro:\n1 Mochila (alto 42cm x ancho 29,5 cm, profundidad 10 cm, logo bordado)\n1 Fórmula 1 sabor Cookies & Cream\n1 Contrato de Distribución\n1 Volante con QR que contiene libro 4, IBO Presentación y Catálogo\n1 Carta de Bienvenida\n1 Tomatodo de 700 ML\n\nCosto: 315.17 Bs.'
#     msg = 'También tengo la lista de los kits en SAM-CAM. Si gustas usa el link /sam_cam para que te la envie.'
#     bot.send_photo(message.from_user.id, url, caption=caption)
#     sleep(5)
#     bot.send_message(message.from_user.id, msg)
    


@bot.message_handler(commands=['interna','externa', 'hmp'])
def nutricion_ext(message):
    msg = "Usa los botones de la parte de abajo por favor"
    if message.text == '/interna':
        tipo = 'interna'
        msg = f"NUTRICIóN {tipo.upper()}. {msg}"
    elif message.text == '/externa':
        tipo = 'externa'
        msg = f"NUTRICIóN {tipo.upper()}. {msg}"
    elif message.text == '/hmp':
        tipo = 'hmp'
        msg = f"{tipo.upper()}. {msg}"
    else:
        tipo = None
    
    cols = 2
    key = ReplyKeyboardMarkup(row_width=cols, resize_keyboard=True, one_time_keyboard=True)
    # key.add('/menu')
    queryset = Categoria.objects.filter(activo=True, tipo=tipo).order_by('nombre')
    nro_items = queryset.count()
    vueltas = int(nro_items//cols)
    impar = True if nro_items % cols > 0 else False

    i = 0
    for _ in range(vueltas):
        btn_izq = str(queryset[i])
        i += 1
        btn_der = str(queryset[i])
        i += 1
        key.row(btn_izq, btn_der)

    if impar:
        key.row(str(queryset[i]))
    
    # Solicita un saludo segun el idioma
    # msg = welcome(message)
    #
    user_id = message.from_user.id
    # Verifica el registro
    save_new_user(message)
    
    # Envia una respuesta
    bot.send_message(user_id, msg, reply_markup=key)

@bot.message_handler(commands=['menu', 'menú'])
def main_menu(message):
    # Pone los botones del menu principal
    user_id = message.from_user.id
    # msg = welcome(message)
    msg = 'Menú principal'
    botones = ['/hmp', '/interna', '/externa']
    key = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True, row_width=1)
    for boton in botones:
        key.add(boton)
    # bot.send_message(user_id, msg, reply_markup=key)
    bot.send_message(chat_id=user_id, text=msg, reply_markup=key)


@bot.message_handler(commands=['start', 'ayuda'])
def start(message):
    
    key = ''

    # Solicita un saludo segun el idioma
    msg = welcome(message)

    # Verifica el registro
    user, created = save_new_user(message)
    
    # sacar imagen de perfil
    # json_dict = bot.get_user_profile_photos(user.user_id)
    # print(f" image profile: {[[y.to_dict() for y in x] for x in json_dict.photos]}")
    # [[print(bot.get_file_url(y.file_id)) for y in x] for x in json_dict.photos]
    # bot.download_file('https://api.telegram.org/file/bot805350267:AAE0kS0hHtPNSxCkhHfMQO-1OJm1LzPp3r0/photos/file_1.jpg')
    # print(bot.get_file('https://api.telegram.org/file/bot805350267:AAE0kS0hHtPNSxCkhHfMQO-1OJm1LzPp3r0/photos/file_1.jpg'))
    # print(f"file_url: {bot.get_file_url('AgACAgEAAxUAAWDOiqanq-clERQ6UPdlXg2hm-GBAAKupzEbszh4LjlW55kJamLC99FuBgAEAQADAgADYwAD_noDAAEfBA')}")
    # print(f" image profile: {bot.get_user_profile_photos(user_id).photos[0][0]}")
    # Envia una respuesta
    bot.send_message(user.user_id, msg, reply_markup=key)
    #
    main_menu(message)


@bot.message_handler(content_types=['text'])
def send_message(message):

    # texto = json.loads(message)
    json_data = message.from_user
    print(f"json_data: {json_data}")
    
    user, created = save_new_user(message)
    
    # Registramos la actividad del usuario
    Activity(user=user, text=message.text).save()

    msg, link, image_url = detail(message)
    # print(f"msg: {msg}, image_url: {image_url}")
    if image_url is None:
        # Enviamos el mensaje
        bot.send_message(user.user_id, msg, reply_markup=link)
    else:
        bot.send_photo(user.user_id, image_url, caption=msg)

def send_m_bot(user, msg):
    bot.send_message(user, msg)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # le damos atributo text a call
    # para enviarlo a la funcion detail
    
    call.text = call.data
    # si existe mensaje mandamos una respuesta
    if call.message:
        # print(f"Message: {call.message}")
        send_message(call)
        # print(f"message: {json.dumps(call.message, indent=4, sort_keys=True)}")
        # text, link, image_url = detail(call)
        # if image_url is None:
        # Enviamos el mensaje
        # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text)
            # bot.edit_message_media(image_url, chat_id=call.message.chat.id, message_id=call.message.message_id)
def response_msg(producto):
    msg = None
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
    try:
        msg_one = "\n{0:25}{1} Bs.\n{2:36}{3} Bs.\n{4:35}{5} Bs.\n{6:33}{7} Bs.".format(
            '> Cliente (sugerido):',
            producto.precios_cliente.cliente,
            'Oro :',
            producto.precios_cliente.oro,
            'Plata :',
            producto.precios_cliente.plata,
            'Bronce :',
            producto.precios_cliente.bronce,
        )
        msg = msg + msg_one
    except: 
        pass
    return msg

def buscar_x_detalles(text):
    prods = Detalles.objects.filter(
                Q(sabor__icontains=text) |
                Q(descripcion__icontains=text),
                activo=True
            )
    try:
        productos = [prod.categoria for prod in prods]
    except:
        productos = None

    return productos

def detail(message):
    text = message.text
    # print(f"TEXT: {text}")
    productos = []
    # calcula y envia el precio del producto solicitado
    msg, link, image = None, None, None

    # Procesamos la respuesta al usurio
    # TODO corregir el codigo de msg para limpiar codigo
    try:
        producto = Categoria.objects.get(nombre__iexact=text, activo=True)
        image = producto.image_url
        msg = response_msg(producto)
        # print(f"Producto: {producto}")
    except:
        
        # print("Buscando por otras caracteristicas")
        productos = Categoria.objects.search(query=text).distinct()
        # print(f"Productos: {productos}")
  
        if not productos or productos is None:
            
            # productos = Categoria.objects.filter(palabrasclave__palabra__icontains=text)
            productos = buscar_x_detalles(text)

        if len(productos) == 1:
            # print("tienes un solo producto")
            producto = productos[0]
            msg = response_msg(producto)
            # print(f"msg: {msg}")
            image = producto.image_url

        elif len(productos) > 1:
            msg = "Tal vez buscas:\n"
            link = InlineKeyboardMarkup()
            for producto in productos:
                link.add(InlineKeyboardButton(text=str(producto), callback_data=str(producto)))
        else:
            # escoge un mensaje aleatorio
            msg = respond(message)
        
        
    return msg, link, image

def user_send_message(request, user_id):
    context, template = {}, 'apps/bot/partials/message-form.html'
    
    if not request.htmx:
        return Http404('404.html')
    try:
        bot_user = User.objects.get(user_id=user_id)
    except:
        bot_user = None

    if bot_user is None:
        return HttpResponse('Not Found')

    form = MessageForm(request.POST or None)
    context = {
        'user'   : bot_user
    }
    if form.is_valid():
        new_message = request.POST.get('message')
        bot.send_message(user_id, text=new_message)
        context['form'] = MessageForm() #type: ignore

    return render(request, template, context)

def enviar_detalle_pedido(request, user_id, pedido_id):
    context, template = {}, 'apps/pedidos/partials/send_order.html'
    detail = ''
    try:
        pedido = Pedido.objects.get(pedido_id=pedido_id)
    except:
        pedido = None

    if pedido is None:
        return HttpResponse('Not Found')
    
    for item in pedido.get_all_items():
        detail += f"{item.categoria} {item.detalles} x{item.cantidad}\n"
    detail += f"\nCantidad: {pedido.get_cart_items}\nPuntos: {pedido.get_cart_points}\nTotal: {pedido.get_cart_total} Bs."
    bot.send_message(user_id, text=detail)
    context = {
        'user_id' : user_id,
        'parent_obj' : pedido
    }

    return render(request, template, context)