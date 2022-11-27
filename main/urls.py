from django.urls import path
from main.views import inicio_view, detalle_ahorro, users_list_view, bot_user_profile, search_view

app_name = 'main'

urlpatterns = [
    path('', inicio_view, name='inicio'),
    path('detalle-ahorro/', detalle_ahorro, name='detalle_ahorro'),
    path('users-list/', users_list_view, name='users_list'),
    path('bot-user-profile/<str:user_id>/', bot_user_profile, name='bot_user_profile'),
    path('bot-user-profile/<str:user_id>/send-message/', bot_user_profile, name='bot_user_message'),
    path('search/', search_view, name='search'),
]
