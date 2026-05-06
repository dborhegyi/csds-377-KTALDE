from django.urls import path
from . import views

app_name = 'KTALDE_web'

urlpatterns = [
    path('startgame/', views.StartGameView.as_view(), name='startgame'),
]