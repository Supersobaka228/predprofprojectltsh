from django.db import models

class Ingredient(models.Model):
    code = models.CharField(max_length=50, unique=True)  # например 'tomato', 'cheese'
    name = models.CharField(max_length=100)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиент"

    def __str__(self):
        return self.name