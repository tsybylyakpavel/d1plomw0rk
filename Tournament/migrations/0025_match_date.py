# Generated by Django 4.2.1 on 2024-06-07 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tournament', '0024_remove_match_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='date',
            field=models.DateTimeField(null=True),
        ),
    ]
