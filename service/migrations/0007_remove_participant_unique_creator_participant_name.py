# Generated by Django 5.2.3 on 2025-07-13 15:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0006_alter_event_name_event_unique_event_name_user_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='participant',
            name='unique_creator_participant_name',
        ),
    ]
