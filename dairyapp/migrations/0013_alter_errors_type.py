# Generated by Django 5.0.7 on 2024-08-23 06:34

import dairyapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dairyapp", "0012_remove_quest_done_remove_quest_errors_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="errors",
            name="type",
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                validators=[dairyapp.models.error_types_validator],
            ),
        ),
    ]
