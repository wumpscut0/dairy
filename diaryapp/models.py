from json import load
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from django.db.models import TextField


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


class Knowledge(models.Model):
    type = models.CharField(default="knowledge", max_length=50, choices=(knowledge_types_validator,), null=True, blank=True)
    text = TextField(max_length=1000, null=True, blank=True)
    class Meta:
        db_table = "dairyapp_knowledge"


class Task(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    planned_datetime = models.DateTimeField(null=True)
    status = models.CharField(default="process", choices=TYPES["task_status"])
    type = models.CharField(default="general", max_length=50, choices=TYPES["tasks"])
    file = models.FileField(upload_to="task/attachments")
    description = TextField(max_length=1000)

def is_resource_available(value):
    try:
        urlopen(value)
    except URLError:
        raise ValidationError(f"resource with url {value} not available")
    
class Resource(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="concepts")
    
    domain = models.CharField(max_length=100)
    status = models.CharField(validators=(is_resource_available,))
    
class Concept(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="concepts")
    
    name = models.CharField(max_length=20)
    theory_level = models.CharField(default="0", choices=)


class Quest(models.Model):
    class Meta:
        ordering = "completed_at", "created_at"
    
        db_table = "diaryapp_quest"

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
