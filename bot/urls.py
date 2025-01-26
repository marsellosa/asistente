from django.urls import path
# from bot.views import UpdateBot, user_send_message, enviar_detalle_pedido
from bot.views import telegram_webhook

app_name = 'bot'

urlpatterns = [
    path('', telegram_webhook, name='update'),
    # path('send/<str:user_id>/', user_send_message, name='send_message'), #type:ignore
    # path('send/<str:user_id>/pedido/<str:pedido_id>/', enviar_detalle_pedido, name='send_pedido'), #type:ignore
]
