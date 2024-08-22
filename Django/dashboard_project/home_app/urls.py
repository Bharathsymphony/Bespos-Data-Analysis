# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logedIn/', views.home_logedIn, name='home_logedIn'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
]