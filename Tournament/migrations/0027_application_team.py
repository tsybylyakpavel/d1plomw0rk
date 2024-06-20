# Generated by Django 4.2.1 on 2024-06-10 18:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Tournament', '0026_alter_application_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='team',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Tournament.team'),
        ),
    ]