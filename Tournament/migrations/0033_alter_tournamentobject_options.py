# Generated by Django 4.2.1 on 2024-06-22 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Tournament', '0032_teammember_birthdate_teammember_middle_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tournamentobject',
            options={'verbose_name': 'tournament', 'verbose_name_plural': 'tournaments'},
        ),
    ]