# Generated manually on 2026-05-04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hr_jobs', '0011_employeetransition'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeetransition',
            name='from_org_unit',
        ),
        migrations.RemoveField(
            model_name='employeetransition',
            name='to_org_unit',
        ),
    ]

