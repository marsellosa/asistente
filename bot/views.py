import json
import logging
import asyncio
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Configurar logging
logger = logging.getLogger(__name__)

# Inicializar la aplicación del bot
application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

# Define comandos para el bot
async def start(update: Update, context):
    """Manejador para el comando /start."""
    user = update.effective_user
    await update.message.reply_text(f"Hola {user.first_name}, ¡bienvenido!")

async def help_command(update: Update, context):
    """Manejador para el comando /help."""
    await update.message.reply_text("¿En qué puedo ayudarte?")

async def echo(update: Update, context):
    """Echo de los mensajes enviados por el usuario."""
    await update.message.reply_text(update.message.text)

# Registrar los manejadores de comandos y mensajes
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Crear un bucle de eventos global
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class TelegramWebhookView(APIView):
    """Vista para manejar las actualizaciones de Telegram."""

    def post(self, request, *args, **kwargs):
        try:
            # Decodifica el JSON recibido desde Telegram
            json_update = request.body.decode("utf-8")
            update_data = json.loads(json_update)
            
            # Convierte el diccionario a un objeto Update
            update = Update.de_json(update_data, application.bot)
            
            # Inicializa la aplicación en el bucle de eventos
            loop.run_until_complete(application.initialize())
            
            # Procesa la actualización en el bucle de eventos
            loop.run_until_complete(application.process_update(update))
            
            return Response({"message": "OK"}, status=200)
        except Exception as e:
            logger.error(f"Error procesando la actualización: {e}. Datos: {json_update}")
            return Response({"error": str(e)}, status=400)