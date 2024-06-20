# Generated by Django 4.2.1 on 2024-06-05 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tournament', '0014_tournamentobject_schedule_generated'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='winner',
            field=models.CharField(choices=[('team1', 'Team 1'), ('team2', 'Team 2'), ('none', 'None')], default='none', max_length=10),
        ),
    ]