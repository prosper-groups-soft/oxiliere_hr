# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_attendance', '0016_employmentscheme_override_recurrence_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyregister',
            name='total_excused',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

