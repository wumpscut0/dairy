from json import load
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models

from django.db.models import TextField
from django.utils.timezone import now


class Day(models.Model):
    created_at = models.DateTimeField()
    content = models.TextField(null=True, blank=True)

class Done(models.Model):
    text = TextField(max_length=1000, null=True, blank=True)
    quest = models.ForeignKey("Quest", on_delete=models.CASCADE, related_name="done")

def errors_types_validator(value):
    with open(Path("errors_types.json").resolve()) as file:
        if value and value not in list(load(file)):
            raise ValidationError("Wrong error type")

class Error(models.Model):
    type = models.CharField(max_length=50, validators=(errors_types_validator,), null=True, blank=True)
    text = TextField(max_length=1000, null=True, blank=True)
    quest = models.ForeignKey("Quest", on_delete=models.CASCADE, related_name="errors")

class Problem(models.Model):
    text = TextField(max_length=1000, null=True, blank=True)
    quest = models.ForeignKey("Quest", on_delete=models.CASCADE, related_name="problems")

class Knowledge(models.Model):
    text = TextField(max_length=1000, null=True, blank=True)
    quest = models.ForeignKey("Quest", on_delete=models.CASCADE, related_name="knowledge")

class Quest(models.Model):
    class Meta:
        ordering = "completed_at", "created_at"
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(null=True)

    origin = models.ForeignKey("Origin", on_delete=models.SET_NULL, null=True)
    theme_description = models.CharField(max_length=500, null=True, blank=True)

    deprecated_total_tasks = models.SmallIntegerField(default=0)
    deprecated_total_completed_tasks = models.SmallIntegerField(default=0)
    deprecated_complete_description = models.TextField(max_length=1000, null=True, blank=True)
    deprecated_knowledge = models.TextField(max_length=1000, null=True, blank=True)

    def clean(self):
        super().clean()
        if self.deprecated_total_tasks < self.deprecated_total_completed_tasks:
            raise ValidationError

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.clean()
        if not self.completed_at and self.done and not self.problems:
            self.completed_at = now()
        self.last_update = now()
        return super().save(force_insert, force_update, using, update_fields
    )


class Origin(models.Model):
    class Meta:
        ordering = "last_extracted_at", "created_at",
    STATUS_CHOICES = [
        ('a', 'actual'),
        ('f', 'frozen'),
        # ('j', 'job'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    last_extracted_at = models.DateTimeField(null=True)
    name = models.CharField(max_length=30, unique=True)
    status = models.CharField(max_length=1, default="a", null=False, choices=STATUS_CHOICES)
    origin = models.CharField(max_length=2048, null=True, blank=True)
