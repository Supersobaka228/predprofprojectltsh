from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0011_alter_meal_count_by_days_alter_meal_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='reviewer_name',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
