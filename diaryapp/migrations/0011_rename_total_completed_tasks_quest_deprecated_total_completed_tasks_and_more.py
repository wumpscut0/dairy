# Generated by Django 5.0.7 on 2024-08-23 04:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("diaryapp", "0010_quest_knowledge"),
    ]

    operations = [
        migrations.RenameField(
            model_name="quest",
            old_name="total_completed_tasks",
            new_name="deprecated_total_completed_tasks",
        ),
        migrations.RenameField(
            model_name="quest",
            old_name="total_tasks",
            new_name="deprecated_total_tasks",
        ),
    ]
