from django.apps import AppConfig


class KtaldeWebConfig(AppConfig):
    name = 'KTALDE_web'

    def ready(self):
        # Defer MQTT setup until after all apps are loaded
        from django.core.management import call_command
        from .views import setup_partner_mqtt
        
        try:
            setup_partner_mqtt()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to initialize MQTT client: {e}")
