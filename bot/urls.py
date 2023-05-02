from django.urls import path
from bot.views import UpdateBot, user_send_message, enviar_detalle_pedido

app_name = 'bot'

urlpatterns = [
    path('', UpdateBot.as_view(), name='update'),
    path('send/<str:user_id>/', user_send_message, name='send_message'),
    path('send/<str:user_id>/pedido/<str:pedido_id>/', enviar_detalle_pedido, name='send_pedido'),
]
