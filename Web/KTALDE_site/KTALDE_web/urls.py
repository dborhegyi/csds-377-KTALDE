from django.urls import path

from . import views

app_name = 'KTALDE_web'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('detail/<int:device_id>/', views.detail, name='detail'),
    path('add/', views.add, name='add'),
]
