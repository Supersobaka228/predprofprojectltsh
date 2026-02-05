from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0015_review_day_default_fill_nulls'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE menu_review SET day = CURRENT_TIMESTAMP WHERE day IS NULL OR day = '' OR day = 'None';",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
