# Generated by Django 4.2.1 on 2024-05-27 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tournament', '0007_alter_match_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournamentobject',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tournamentobject',
            name='sport',
            field=models.CharField(choices=[('football', 'Футбол'), ('tennis', 'Теннис'), ('boxing', 'Бокс'), ('badminton', 'Бадминтон'), ('volleyball', 'Волейбол'), ('basketball', 'Баскетбол'), ('handball', 'Гандбол'), ('esports', 'Киберспорт'), ('hockey', 'Хоккей'), ('rugby', 'Регби')], default='football', max_length=20),
        ),
        migrations.AddField(
            model_name='tournamentobject',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tournamentobject',
            name='tournament_type',
            field=models.CharField(choices=[('SE', 'Олимпийская система'), ('DE', 'С двойным выбыванием')], default='SE', max_length=2),
        ),
    ]
