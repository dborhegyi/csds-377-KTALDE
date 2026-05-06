from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

DEFAULT_USER: str = 'parked_device_user'


def get_parked_user() -> User:
    return get_user_model().objects.get_or_create(username=DEFAULT_USER)[0]


class Lampi(models.Model):
    name = models.CharField(max_length=50, default="My LAMPI")
    device_id = models.CharField(max_length=12, primary_key=True)
    user = models.ForeignKey(User,
                             on_delete=models.SET(get_parked_user))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "{}: {}".format(self.device_id, self.name)


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
