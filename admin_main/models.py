from django.db import models
from decimal import Decimal

from menu.models import Meal
from users.models import User
from menu.models import Ingredient


# Create your models here.

class BuyOrder(models.Model):
    id = models.AutoField(primary_key=True)
    summ = models.IntegerField(default=1000)
    items = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(default='ns', max_length=10)

    @property
    def summ_rub(self):
        return Decimal(self.summ) / Decimal('100')

class Notification(models.Model):
    text = models.CharField(max_length=255)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class Food_count(models.Model):
    id = models.AutoField(primary_key=True)
    food_id = models.ForeignKey(Meal, on_delete=models.CASCADE)
    num = models.IntegerField()

