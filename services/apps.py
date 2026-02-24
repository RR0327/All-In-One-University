from django.apps import AppConfig


class ServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services"
    verbose_name = "University Campus Services"

    def ready(self):
        # This imports the signals to ensure they are registered
        import services.models
