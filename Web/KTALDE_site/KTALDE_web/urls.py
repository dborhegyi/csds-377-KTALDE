from django.urls import path, re_path

from . import views

app_name = 'KTALDE_web'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    re_path(r'^device/(?P<device_id>[0-9a-fA-F]+)$',
            views.DetailView.as_view(), name='detail'),
    path('ingame/', views.view_pdf, name='ingame'),
]

