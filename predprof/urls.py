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
from django.views.generic import RedirectView

import chef_main.views
import menu.views
import users.views
import admin_main.views

urlpatterns = [
    path('', RedirectView.as_view(url='/menu/', permanent=False)),
    path('register/', users.views.register, name='register'),
    path('login/', users.views.login_f, name='login'),
    path('admin_login/', users.views.login_admin, name='admin_login'),
    path('logout/', users.views.logout_f, name='logout'),
    path('logout_menu/', users.views.logout_menu, name='logout_menu'),
    path('menu/', menu.views.menu, name='menu'),
    path('menu/confirm_order/', menu.views.confirm_order, name='confirm_order'),
    path('menu/update_allergens/', menu.views.update_allergens, name='update_allergens'),
    path('menu/purchase-subscription/', users.views.purchase_subscription, name='purchase_subscription'),
    path('admin_main/', admin_main.views.admin, name='admin_main'),
    path('admin_main/buyorders/', admin_main.views.buyorders_by_date, name='buyorders_by_date'),
    path('balance/topup/', users.views.topup_balance, name='topup_balance'),
    path('chef_main/', chef_main.views.chef, name='chef_main'),
    path('admin/', admin.site.urls),
    path('update-order-status/', admin_main.views.update_order_status, name='update_order_status'),
    path('chef_main/api/update-issued-count/', chef_main.views.update_issued_count, name='update_issued_count'),
    path('admin_main/report/general/', admin_main.views.admin_report_general, name='admin_report_general'),
    path('admin_main/report/costs/', admin_main.views.admin_report_costs, name='admin_report_costs'),
    path('chef_main/api/get-meal-dat/', chef_main.views.get_meal_data, name='get_meal_data'),

]
