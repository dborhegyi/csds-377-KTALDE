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
from django.urls import path, include
from KTALDE_web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('KTALDE_web.urls')),
    path('startgame/', views.StartGameView.as_view(), name='startgame'),
    path('ingame/', views.ingame, name='ingame'),
    # path('ingame/pdf/', views.view_pdf, name='ingame_pdf'),
]