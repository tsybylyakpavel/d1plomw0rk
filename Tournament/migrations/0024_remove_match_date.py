# Generated by Django 4.2.1 on 2024-06-07 20:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Tournament', '0023_remove_tournamentobject_winner_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='date',
        ),
    ]
