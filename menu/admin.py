from django.contrib import admin

from .models import Allergen, DayOrder, Meal, MenuItem, MealIngredient, Order


@admin.register(DayOrder)
class DayOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'order')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'time', 'price')
    list_filter = ('category',)
    search_fields = ('category', 'time')
    filter_horizontal = ('meals',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('day', 'user', 'name', 'time', 'price')


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'sort_order')
    list_filter = ('sort_order',)
    search_fields = ('code', 'name')
    ordering = ('sort_order', 'name')


class MealIngredientInline(admin.TabularInline):
    model = MealIngredient
    extra = 1


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'weight', 'calories', 'ingredients_summary')
    search_fields = ('name',)
    filter_horizontal = ('allergens',)
    inlines = (MealIngredientInline,)

    def ingredients_summary(self, obj):
        return obj.ingredients_with_mass

    ingredients_summary.short_description = 'Ингредиенты'
