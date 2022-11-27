from django.urls import path
from bot.views import UpdateBot, user_send_message

app_name = 'bot'

urlpatterns = [
    path('', UpdateBot.as_view(), name='update'),
    path('send/<int:user_id>/', user_send_message, name='send_message'),
]
