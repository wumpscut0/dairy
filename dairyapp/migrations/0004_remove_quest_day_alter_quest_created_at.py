# Generated by Django 5.0.7 on 2024-08-08 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dairyapp", "0003_day_quest_day"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="quest",
            name="day",
        ),
        migrations.AlterField(
            model_name="quest",
            name="created_at",
            field=models.DateTimeField(),
        ),
    ]
