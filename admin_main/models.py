from django.db import models
from decimal import Decimal
from django.utils import timezone

from users.models import User
from menu.models import Ingredient


# Create your models here.

class BuyOrder(models.Model):
    id = models.AutoField(primary_key=True)
    summ = models.IntegerField(default=1000)
    items = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    date = models.DateTimeField(default=timezone.now)
    status = models.CharField(default='ns', max_length=10)

    @property
    def summ_rub(self):
        return Decimal(self.summ) / Decimal('100')

class Notification(models.Model):
    RECIPIENT_ALL = "all"
    RECIPIENT_ADMIN = "admin"
    RECIPIENT_CHEF = "chef"
    RECIPIENT_USER = "user"

    RECIPIENT_CHOICES = (
        (RECIPIENT_ALL, "All"),
        (RECIPIENT_ADMIN, "Admin"),
        (RECIPIENT_CHEF, "Chef"),
        (RECIPIENT_USER, "User"),
    )

    recipient_type = models.CharField(
        max_length=10,
        choices=RECIPIENT_CHOICES,
        default=RECIPIENT_ALL,
    )
    recipient_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    title = models.CharField(max_length=120)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



