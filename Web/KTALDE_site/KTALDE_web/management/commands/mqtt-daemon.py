import re
from typing import Any, Optional

from paho.mqtt.client import (Client, CallbackAPIVersion, ConnectFlags,
                              MQTTMessage)
from paho.mqtt.reasoncodes import ReasonCode
from paho.mqtt.properties import Properties
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.conf import settings
from lampi_web.models import Lampi


MQTT_BROKER_RE_PATTERN: str = (r'\$sys\/broker\/connection\/'
                               r'(?P<device_id>[0-9a-f]*)_broker/state')


def device_association_topic(device_id: str) -> str:
    return 'devices/{}/lamp/associated'.format(device_id)


class Command(BaseCommand):
    help = 'Long-running Daemon Process to Integrate MQTT Messages with Django'
    client: Client

    def _create_default_user_if_needed(self) -> None:
        # make sure the user account exists that holds all new devices
        try:
            User.objects.get(username=settings.DEFAULT_USER)
        except User.DoesNotExist:
            print("Creating user {} to own new LAMPI devices".format(
                settings.DEFAULT_USER))
            new_user = User()
            new_user.username = settings.DEFAULT_USER
            new_user.password = '123456'
            new_user.is_active = False
            new_user.save()

    def _on_connect(self, client: Client, userdata: Any,
                    flags: ConnectFlags, reason_code: ReasonCode,
                    properties: Optional[Properties]) -> None:
        self.client.message_callback_add('$SYS/broker/connection/+/state',
                                         self._device_broker_status_change)
        self.client.subscribe('$SYS/broker/connection/+/state')

    def _create_mqtt_client_and_loop_forever(self) -> None:
        self.client = Client(callback_api_version=CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.connect('localhost', port=50001)
        self.client.loop_forever()

    def _device_broker_status_change(self, client: Client, userdata: Any,
                                     message: MQTTMessage) -> None:
        print("RECV: '{}' on '{}'".format(message.payload, message.topic))
        # message payload has to treated as type "bytes" in Python 3
        if message.payload == b'1':
            # broker connected
            results = re.search(MQTT_BROKER_RE_PATTERN, message.topic.lower())
            if results is None:
                return
            device_id = results.group('device_id')
            try:
                device = Lampi.objects.get(device_id=device_id)
                print("Found {}".format(device))
            except Lampi.DoesNotExist:
                # this is a new device - create new record for it
                new_device = Lampi(device_id=device_id)
                uname = settings.DEFAULT_USER
                new_device.user = User.objects.get(username=uname)
                new_device.save()
                print("Created {}".format(new_device))

    def handle(self, *args: Any, **options: Any) -> None:
        self._create_default_user_if_needed()
        self._create_mqtt_client_and_loop_forever()