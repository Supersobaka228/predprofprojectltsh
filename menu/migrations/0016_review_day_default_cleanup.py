from django.db import migrations, models
from django.utils import timezone


def fill_null_review_day(apps, schema_editor):
    Review = apps.get_model('menu', 'Review')
    Review.objects.filter(day__isnull=True).update(day=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0015_review_day_default_fill_nulls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='day',
            field=models.DateTimeField(default=timezone.now),
        ),
        migrations.RunPython(fill_null_review_day, migrations.RunPython.noop),
    ]
