from django.apps import AppConfig

class AuditsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audits'

    def ready(self):
        """Forces Django to import and connect signals when the environment initializes."""
        import audits.signals