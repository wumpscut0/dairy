from json import load
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models

from django.db.models import TextField

TYPES_PATH = Path("types.json").resolve()
with open(TYPES_PATH) as file:
    TYPES = load(file)


def task_types_validator(value):
    if value and value not in TYPES["tasks"]:
        raise ValidationError("Wrong type")


def error_types_validator(value):
    if value and value not in TYPES["errors"]:
        raise ValidationError("Wrong type")


def problem_types_validator(value):
    if value and value not in TYPES["problems"]:
        raise ValidationError("Wrong type")


def knowledge_types_validator(value):
    if value and value not in TYPES["knowledge"]:
        raise ValidationError("Wrong type")


class Day(models.Model):
    created_at = models.DateTimeField()
    content = models.TextField(null=True, blank=True)
    class Meta:
        db_table = "dairyapp_day"


class Error(models.Model):
    type = models.CharField(
        max_length=50, validators=(error_types_validator,), null=True, blank=True
    )
    text = TextField(max_length=1000, null=True, blank=True)
    quest = models.ForeignKey("Quest", on_delete=models.CASCADE, related_name="errors")
    class Meta:
        db_table = "dairyapp_error"


class Problem(models.Model):
    type = models.CharField(
        max_length=50, validators=(problem_types_validator,), null=True, blank=True
    )
    text = TextField(max_length=1000, null=True, blank=True)
    quest = models.ForeignKey(
        "Quest", on_delete=models.CASCADE, related_name="problems"
    )
    class Meta:
        db_table = "dairyapp_problem"


class Knowledge(models.Model):
    type = models.CharField(
        max_length=50, validators=(knowledge_types_validator,), null=True, blank=True
    )
    text = TextField(max_length=1000, null=True, blank=True)
    quest = models.ForeignKey(
        "Quest", on_delete=models.CASCADE, related_name="knowledge"
    )
    class Meta:
        db_table = "dairyapp_knowledge"


class Task(models.Model):
    status = models.SmallIntegerField(default=0)
    type = models.CharField(max_length=50, validators=(task_types_validator,))
    text = TextField(max_length=1000)
    quest = models.ForeignKey("Quest", on_delete=models.CASCADE, related_name="tasks")
    
    class Meta:
        db_table = "dairyapp_task"


class Quest(models.Model):
    class Meta:
        ordering = "completed_at", "created_at"
    
        db_table = "dairyapp_quest"

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(null=True)

    origin = models.ForeignKey("Origin", on_delete=models.SET_NULL, null=True)
    theme = models.CharField(max_length=100, null=True, blank=True)

    deprecated_total_tasks = models.SmallIntegerField(default=0)
    deprecated_total_completed_tasks = models.SmallIntegerField(default=0)
    deprecated_complete_description = models.TextField(
        max_length=1000, null=True, blank=True
    )
    deprecated_knowledge = models.TextField(max_length=1000, null=True, blank=True)


class Origin(models.Model):
    class Meta:
        ordering = (
            "last_extracted_at",
            "created_at",
        )

        db_table = "dairyapp_origin"
        

    STATUS_CHOICES = [
        ("a", "actual"),
        ("f", "frozen"),
        # ('j', 'job'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    last_extracted_at = models.DateTimeField(null=True)
    name = models.CharField(max_length=30, unique=True)
    status = models.CharField(
        max_length=1, default="a", null=False, choices=STATUS_CHOICES
    )
    origin = models.CharField(max_length=2048, null=True, blank=True)
