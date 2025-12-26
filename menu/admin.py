"""from django.contrib import admin
from .models import MenuItem, DayOrder


@admin.register(DayOrder)
class DayOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'order')
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'time', 'price')"""