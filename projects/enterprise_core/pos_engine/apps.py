from django.apps import AppConfig

class PosEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pos_engine'

    def ready(self):
        import config.signals