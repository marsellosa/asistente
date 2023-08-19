from django.apps import AppConfig


class ComandaConfig(AppConfig):
    name = 'comanda'

    def ready(self):
        from comanda import signals