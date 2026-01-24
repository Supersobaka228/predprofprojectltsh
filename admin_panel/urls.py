from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_admin, name='login_admin'),
    path('', views.admin_home, name='admin_home'),  # главная админки после входа
]