# Generated by Django 5.0.7 on 2024-08-18 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dairyapp", "0007_quest_knowledge"),
    ]

    operations = [
        migrations.AddField(
            model_name="quest",
            name="last_update",
            field=models.DateTimeField(null=True),
        ),
    ]
