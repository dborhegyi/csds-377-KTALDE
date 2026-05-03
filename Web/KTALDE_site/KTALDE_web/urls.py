from django.urls import path, re_path

from . import views

app_name = 'KTALDE_web'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('ingame/', views.view_pdf, name='ingame'),
]

