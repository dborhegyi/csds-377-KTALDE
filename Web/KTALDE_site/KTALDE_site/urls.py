"""KTALDE_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from KTALDE_web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('startgame/', views.StartGameView.as_view(), name='startgame'),
    path('ingame/', views.IndexView.as_view(), name='index'),
    path('ingame/pdf-file/', views.MyPDFView.as_view(response_type='pdf'), name='pdf-file'),
    path('ingame/pdf-html/', views.MyPDFView.as_view(response_type='html'), name='pdf-html'),
    path('ingame/pdf-download/', views.MyPDFView.as_view(response_type='download'), name='pdf-download'),
]
