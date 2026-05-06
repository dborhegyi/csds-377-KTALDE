from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
import json
import paho.mqtt.publish
import secrets
import string


def get_parked_user() -> User:
    return get_user_model().objects.get_or_create(username=settings.DEFAULT_USER)[0]


def generate_association_code() -> str:
    """Generate a 6-character association code."""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(6))



class Lampi(models.Model):
    name = models.CharField(max_length=50, default="My LAMPI")
    device_id = models.CharField(max_length=12, primary_key=True)
    association_code = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        null=True,
        db_index=True
    )
    user = models.ForeignKey(User,
                             on_delete=models.SET(get_parked_user))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "{}: {}".format(self.device_id, self.name)

    def save(self, *args, **kwargs):
        """Auto-generate association code if not set."""
        if not self.association_code:
            self.association_code = generate_association_code()
        super().save(*args, **kwargs)


class Game(models.Model):
    game_id = models.CharField(max_length=50, unique=True)
    display_lampi = models.ForeignKey(Lampi, related_name='display_games', on_delete=models.CASCADE)  # Lampi that shows the color
    match_lampi = models.ForeignKey(Lampi, related_name='match_games', on_delete=models.CASCADE)    # Lampi whose player matches with sliders
    target_color = models.JSONField()  # {'h': float, 's': float, 'b': float}
    display_submitted = models.BooleanField(default=False)
    match_submitted = models.BooleanField(default=False)
    display_state = models.JSONField(null=True)
    match_state = models.JSONField(null=True)
    status = models.CharField(max_length=20, default='waiting')  # 'waiting', 'active', 'completed'
    winner = models.CharField(max_length=10, null=True)  # 'match' or None
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
            hostname=settings.MQTT_BROKER_HOST,
            port=settings.MQTT_BROKER_PORT,
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
            hostname=settings.MQTT_BROKER_HOST,
            port=settings.MQTT_BROKER_PORT,
            )
