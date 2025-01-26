from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('bot1075118916/', include('bot.urls')),
    path('comanda/', include('comanda.urls')),
    path('consumos/', include('consumos.urls')),
    path('main/', include('main.urls')),
    path('operadores/', include('operadores.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('personas/', include('persona.urls')),
    path('prepagos/', include('prepagos.urls')),
    path('productos/', include('productos.urls')),
    path('recetas/', include('recetas.urls')),
    path('reportes/', include('reportes.urls')),
    path('socios/', include('socios.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
