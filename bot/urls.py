from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from bot.views import *

app_name = 'bot'

urlpatterns = [
    # path('', csrf_exempt(TelegramWebhookView.as_view()), name='update'),
    path('send/<str:user_id>/', user_send_message, name='send_message'), #type:ignore
    path('send/<str:user_id>/pedido/<str:pedido_id>/', enviar_detalle_pedido, name='send_pedido'), #type:ignore
]
