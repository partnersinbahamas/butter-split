# Generated by Django 5.2.3 on 2025-07-13 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0004_alter_event_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='session_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
