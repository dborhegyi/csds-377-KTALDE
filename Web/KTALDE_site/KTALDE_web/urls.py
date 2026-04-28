from django.urls import path

from . import views

app_name = 'KTALDE_web'

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:device_id>/', views.detail, name='detail'),
    path('add/', views.add, name='add'),
]
