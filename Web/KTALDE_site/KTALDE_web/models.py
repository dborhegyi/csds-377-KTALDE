from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from uuid import uuid4
import json
import paho.mqtt.publish

DEFAULT_USER: str = 'parked_device_user'


def get_parked_user() -> User:
    return get_user_model().objects.get_or_create(username=DEFAULT_USER)[0]


def generate_association_code() -> str:
    return uuid4().hex



class Lampi(models.Model):
    name = models.CharField(max_length=50, default="My LAMPI")
    device_id = models.CharField(max_length=12, primary_key=True)
    user = models.ForeignKey(User,
                             on_delete=models.SET(get_parked_user))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "{}: {}".format(self.device_id, self.name)

    def _generate_device_association_topic(self) -> str:
        return 'devices/{}/lamp/associated'.format(self.device_id)

    def publish_unassociated_msg(self) -> None:
        # send association MQTT message
        assoc_msg = {}
        assoc_msg['associated'] = False
        assoc_msg['code'] = self.association_code
        paho.mqtt.publish.single(
            self._generate_device_association_topic(),
            json.dumps(assoc_msg),
            client_id=settings.MQTT_DAEMON_USERNAME,
            auth={'username': settings.MQTT_DAEMON_USERNAME,
                  'password': settings.MQTT_DAEMON_PASSWORD},
            qos=2,
            retain=True,
            hostname="localhost",
            port=1883,
            )

    def associate_and_publish_associated_msg(self, user: User) -> None:
        # update Lampi instance with new user
        self.user = user
        self.save()
        # publish associated message
        assoc_msg = {}
        assoc_msg['associated'] = True
        paho.mqtt.publish.single(
            self._generate_device_association_topic(),
            json.dumps(assoc_msg),
            client_id=settings.MQTT_DAEMON_USERNAME,
            auth={'username': settings.MQTT_DAEMON_USERNAME,
                  'password': settings.MQTT_DAEMON_PASSWORD},
            qos=2,
            retain=True,
            hostname="localhost",
            port=50002,
            )
