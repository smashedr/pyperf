from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = 'home'
    verbose_name = 'Home'

    def ready(self):
        from . import signals
