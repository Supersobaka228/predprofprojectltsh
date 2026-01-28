from django.db import models

from users.models import User


# Create your models here.

class BuyOrder(models.Model):
    id = models.AutoField(primary_key=True)
    summ = models.IntegerField()
    items = models.CharField(max_length=200)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    text = models.CharField(max_length=255)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)