from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0013_review_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='day',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
