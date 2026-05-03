from django.urls import path, re_path

from . import views
from my_app.views import MyPDFView

app_name = 'KTALDE_web'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    re_path(r'^device/(?P<device_id>[0-9a-fA-F]+)$',
            views.DetailView.as_view(), name='detail'),
    path('pdf-file/', MyPDFView.as_view(response_type='pdf'), name='pdf-file'),
    path('pdf-html/', MyPDFView.as_view(response_type='html'), name='pdf-html'),
    path('pdf-download/', MyPDFView.as_view(response_type='download'), name='pdf-download'),
]
