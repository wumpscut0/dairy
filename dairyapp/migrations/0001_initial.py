# Generated by Django 5.0.7 on 2024-07-31 05:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Origin",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_extracted_at", models.DateTimeField(null=True)),
                ("name", models.CharField(max_length=30, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("a", "actual"), ("f", "frozen")],
                        default="a",
                        max_length=1,
                    ),
                ),
                ("origin", models.CharField(blank=True, max_length=2048, null=True)),
            ],
            options={
                "ordering": ("last_extracted_at", "created_at"),
            },
        ),
        migrations.CreateModel(
            name="Quest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "complete_description",
                    models.TextField(blank=True, max_length=1000, null=True),
                ),
                (
                    "origin",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="dairyapp.origin",
                    ),
                ),
            ],
            options={
                "ordering": ("completed_at", "created_at"),
            },
        ),
    ]
