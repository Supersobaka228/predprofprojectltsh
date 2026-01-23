from django.contrib import admin

from .models import Allergen, DayOrder, Meal, MenuItem


@admin.register(DayOrder)
class DayOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'order')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'time', 'price')
    list_filter = ('category',)
    search_fields = ('category', 'time')
    filter_horizontal = ('meals',)


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'sort_order')
    list_filter = ('sort_order',)
    search_fields = ('code', 'name')
    ordering = ('sort_order', 'name')


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'weight', 'calories')
    search_fields = ('name',)
    filter_horizontal = ('allergens',)
