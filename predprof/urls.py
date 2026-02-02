"""
URL configuration for predprof project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path

import chef_main.views
import menu.views
import users.views
import admin_main.views

urlpatterns = [
    path('register/', users.views.register, name='register'),
    path('login/', users.views.login_f, name='login'),
    path('menu/', menu.views.menu, name='menu'),
    path('menu/update_allergens/', menu.views.update_allergens, name='update_allergens'),
    path('admin_main/', admin_main.views.admin, name='admin_main'),
    path('balance/topup/', users.views.topup_balance, name='topup_balance'),
    path('chef_main/', chef_main.views.chef, name='chef_main'),
    path('admin/', admin.site.urls),
    path('update-order-status/', admin_main.views.update_order_status, name='update_order_status'),

]
