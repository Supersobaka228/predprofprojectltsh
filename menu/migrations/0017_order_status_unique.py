from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('menu', '0016_review_day_cleanup'),
        ('menu', '0016_review_day_default_cleanup'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[('ordered', 'Заказано'), ('confirmed', 'Подтверждено')],
                default='ordered',
                max_length=12,
            ),
        ),
        migrations.AddConstraint(
            model_name='order',
            constraint=models.UniqueConstraint(
                fields=('user', 'name', 'day'),
                name='uniq_order_user_item_day',
            ),
        ),
    ]
