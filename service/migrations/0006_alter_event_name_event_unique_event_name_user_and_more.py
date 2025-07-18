# Generated by Django 5.2.3 on 2025-07-13 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0005_event_session_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AddConstraint(
            model_name='event',
            constraint=models.UniqueConstraint(condition=models.Q(('owner__isnull', False)), fields=('name', 'owner'), name='unique_event_name_user'),
        ),
        migrations.AddConstraint(
            model_name='event',
            constraint=models.UniqueConstraint(condition=models.Q(('owner__isnull', True)), fields=('name', 'session_id'), name='unique_event_name_session'),
        ),
    ]
