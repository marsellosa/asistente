# bot/views.py
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Configura el token del bot y la aplicación
TELEGRAM_TOKEN = config('TOKEN')
application = Application.builder().token(TELEGRAM_TOKEN).build()

logger = logging.getLogger(__name__)

# Define las funciones de comando como en tu código original
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(rf"Hi {user.mention_html()}!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

# Agrega los manejadores de comandos
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Vista para recibir las actualizaciones
@csrf_exempt
async def telegram_webhook(request):
    if request.method == "POST":
        # Convierte el JSON de Telegram en un objeto Update
        update = Update.de_json(request.json(), application.bot)
        # Procesa el update con la aplicación de Telegram
        await application.update_queue.put(update)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Método no permitido"}, status=405)
