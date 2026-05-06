from django.apps import AppConfig
from .views import setup_partner_mqtt


class KtaldeWebConfig(AppConfig):
    name = 'KTALDE_web'

    def ready(self):
        setup_partner_mqtt()
