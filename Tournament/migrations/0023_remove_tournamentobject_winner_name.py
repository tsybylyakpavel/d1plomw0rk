# Generated by Django 4.2.1 on 2024-06-07 19:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Tournament', '0022_tournamentobject_winner_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournamentobject',
            name='winner_name',
        ),
    ]