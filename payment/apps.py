from django.apps import AppConfig

class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payment'

    def ready(self):
        # Import signals
        import payment.signals