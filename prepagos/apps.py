from django.apps import AppConfig


class PrepagosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prepagos'

    def ready(self):
        from prepagos import signals