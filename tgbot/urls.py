from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    # path('accounts/', include('allauth.urls')),
    path('bot1075118916/', include('bot.urls')),
    # path('clubes/', include('clubes.urls')),
    path('comanda/', include('comanda.urls')),
    path('consumos/', include('consumos.urls')),
    # path('evaluaciones/', include('evaluaciones.urls')),
    # path('finanzas/', include('finanzas.urls')),
    path('main/', include('main.urls')),
    # path('notificaciones/', include('notificaciones.urls')),
    path('operadores/', include('operadores.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('personas/', include('persona.urls')),
    path('prepagos/', include('prepagos.urls')),
    path('productos/', include('productos.urls')),
    path('recetas/', include('recetas.urls')),
    path('reportes/', include('reportes.urls')),
    path('socios/', include('socios.urls')),
    path('whatsapp/', include('whatsapp.urls')),
] #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])