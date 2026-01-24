from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User


class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
    ]

    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    time = models.CharField(max_length=20)
    price = models.IntegerField()
    id = models.AutoField(primary_key=True)

    # Связка с блюдами
    meals = models.ManyToManyField('Meal', blank=True, related_name='menu_items')

    icon = models.CharField(max_length=255)

    calories = models.IntegerField()
    proteins = models.IntegerField()
    fats = models.IntegerField()
    carbs = models.IntegerField()

    @property
    def meals_limit3(self):
        """Первые 3 связанных Meal."""
        return list(self.meals.all()[:3])

    @property
    def min_des_list(self):
        """Список названий блюд (Meal.name), максимум 3."""
        return [m.name for m in self.meals_limit3]

    @property
    def max_des_list(self):
        """Список описаний блюд (Meal.description), максимум 3."""
        return [m.description for m in self.meals_limit3]

    @property
    def allergens_list(self):
        """Уникальные названия аллергенов (Allergen.name) из Meal.allergens для первых 3 Meal."""
        names = []
        seen = set()
        for meal in self.meals_limit3:
            for allergen in meal.allergens.all():
                if allergen.name not in seen:
                    seen.add(allergen.name)
                    names.append(allergen.name)
        return names

    def __str__(self):
        return f"{self.category} {self.time} - {self.price}₽"


class DayOrder(models.Model):
    day = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)])
    order = models.JSONField(default=list, blank=True)


class Review(models.Model):
    CATEGORY_CHOICES = [
        ('Завтрак', 'Завтрак'),
        ('Обед', 'Обед'),
    ]
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    day = models.CharField()
    text = models.TextField()
    stars_count = models.IntegerField(default=3)


class Order(models.Model):
    time = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    day = models.CharField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)


# ИЗМЕНЕНИЯ, НОВЫЕ МОДЕЛИ
class Allergen(models.Model):
    code = models.CharField(max_length=50, unique=True)  # например 'gluten', 'nuts'
    name = models.CharField(max_length=200)               # отображаемое имя 'Глютен', 'Орехи'
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Аллерген"
        verbose_name_plural = "Аллергены"

    def __str__(self):
        return self.name


class Meal(models.Model):
    name = models.CharField(max_length=255)
    weight = models.IntegerField()
    calories = models.IntegerField()
    allergens = models.ManyToManyField(Allergen, blank=True, related_name='meals')
    description = models.TextField()

    def __str__(self):
        return self.name
