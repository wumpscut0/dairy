# Generated by Django 5.0.7 on 2024-08-22 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "dairyapp",
            "0009_rename_complete_description_quest_deprecated_complete_description_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="quest",
            name="knowledge",
            field=models.JSONField(default=list),
        ),
    ]