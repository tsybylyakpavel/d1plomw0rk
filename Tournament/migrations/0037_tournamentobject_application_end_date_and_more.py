# Generated by Django 4.2.1 on 2024-06-23 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tournament', '0036_alter_match_result_team1_alter_match_result_team2'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournamentobject',
            name='application_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tournamentobject',
            name='application_start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
