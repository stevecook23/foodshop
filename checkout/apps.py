"""Apps for checkout app."""
from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'checkout'
    verbose_name = 'Checkout'

    def ready(self):
        import checkout.signals