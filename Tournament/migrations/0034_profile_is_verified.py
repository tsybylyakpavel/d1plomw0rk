# Generated by Django 4.2.1 on 2024-06-22 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tournament', '0033_alter_tournamentobject_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]