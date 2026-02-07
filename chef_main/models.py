from django.db import models

LOW_STOCK_THRESHOLD = 10000

class Ingredient(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)  # например 'tomato', 'cheese'
    name = models.CharField(max_length=100)
    sort_order = models.PositiveSmallIntegerField(default=0)
    remains = models.IntegerField(default=100)
    low_stock_notified = models.BooleanField(default=False)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиент"

    def __str__(self):
        return self.name