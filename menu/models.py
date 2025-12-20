from django.db import models

from predprof import settings


class Dish(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    allergens = models.TextField(blank=True, null=True)
    calories = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
    ]

    DAY_CHOICES = [
        ('monday', 'Понедельник'),
        ('tuesday', 'Вторник'),
        ('wednesday', 'Среда'),
        ('thursday', 'Четверг'),
        ('friday', 'Пятница'),
        ('saturday', 'Суббота'),
    ]

    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPE_CHOICES)
    date = models.DateField()
    dishes = models.ManyToManyField(Dish, through='MenuDish')


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField()
    date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dish = models.ForeignKey(settings.AUTH_DISH_MODEL, on_delete=models.CASCADE)




