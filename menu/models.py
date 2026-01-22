from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
    ]
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    time = models.CharField(max_length=20)
    price = models.IntegerField()
    id = models.AutoField(primary_key=True)

    min_des = models.JSONField(default=list, blank=True)
    max_des = models.JSONField(default=list, blank=True)
    allergens = models.JSONField(default=list, blank=True)

    icon = models.CharField(max_length=255)

    calories = models.IntegerField()
    proteins = models.IntegerField()
    fats = models.IntegerField()
    carbs = models.IntegerField()

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