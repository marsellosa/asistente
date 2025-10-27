from django.urls import path
from . import views

app_name = 'whatsapp'

urlpatterns = [
    path('messages/', views.messages_view, name='messages'),
    path('response/', views.response_message_view, name='response'),
    path('send-message/', views.send_message_view, name='send_message'),

]