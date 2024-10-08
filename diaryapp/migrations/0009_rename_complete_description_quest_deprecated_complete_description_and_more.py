# Generated by Django 5.0.7 on 2024-08-22 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("diaryapp", "0008_quest_last_update"),
    ]

    operations = [
        migrations.RenameField(
            model_name="quest",
            old_name="complete_description",
            new_name="deprecated_complete_description",
        ),
        migrations.RenameField(
            model_name="quest",
            old_name="knowledge",
            new_name="deprecated_knowledge",
        ),
        migrations.AddField(
            model_name="quest",
            name="done",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="quest",
            name="problems",
            field=models.JSONField(default=list),
        ),
    ]
