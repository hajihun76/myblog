# busorder/apps.py
from django.apps import AppConfig

class BusorderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'busorder'

    def ready(self):
        from . import signals  # Permission은 signals.py에서만 import
