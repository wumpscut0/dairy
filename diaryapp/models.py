from urllib.error import URLError
from urllib.request import urlopen

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from diaryapp.types import TYPES


class Note(models.Model):
    created_at = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    
    note = models.TextField(null=True, blank=True)

class Target(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    completed_at = models.DateTimeField(null=True)
    status = models.CharField(default="process", choices=TYPES["target_status"])
    type = models.CharField(default="general", choices=TYPES["targets"])
    priority = models.CharField(default="medium", choices=TYPES["priority"])
    description = models.TextField(max_length=1000)
    planned_datetime = models.DateTimeField(null=True)
    file = models.FileField(upload_to="tasks/attachments")
    

def is_resource_available(value):
    try:
        urlopen(value)
    except URLError:
        raise ValidationError(f"resource with url {value} not available")
    
class Resource(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resources")
    
    domain = models.CharField(max_length=100, validators=(is_resource_available,))
    status = models.BooleanField(default=True)

class Book(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="concepts")
    
    author = models.CharField(max_length=30)
    name = models.CharField(max_length=15)
    file = models.FileField(upload_to="books", null=True)
    comprehension = models.CharField(default="unknown", choices=TYPES["comprehension"])
    
    class Meta:
        unique_together = ("author", "name")
    
class Area(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="concepts")

    name = models.CharField(max_length=20)
    type = models.CharField(default="other", choices=TYPES["area"])
    grade = models.CharField(default="0", choices=TYPES["grade"])
    experience = models.TextField(max_length=1000, null=True, blank=True)
    
    
    

    
def params_factory():
    return {
        "push-ups": 0,
        "squats": 0,
        "bar": 0, #s
        "pull-ups": 0,
        "run": 0, #m
        
    }

class Profile(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    
    params = models.JSONField(default=params_factory)

#
# class Quest(models.Model):
#     class Meta:
#         ordering = "completed_at", "created_at"
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
#     last_update = models.DateTimeField(null=True)
#
#     origin = models.ForeignKey("Origin", on_delete=models.SET_NULL, null=True)
#     theme = models.CharField(max_length=100, null=True, blank=True)
#
#     deprecated_total_tasks = models.SmallIntegerField(default=0)
#     deprecated_total_completed_tasks = models.SmallIntegerField(default=0)
#     deprecated_complete_description = models.TextField(
#         max_length=1000, null=True, blank=True
#     )
#     deprecated_knowledge = models.TextField(max_length=1000, null=True, blank=True)


# class Origin(models.Model):
#     class Meta:
#         ordering = (
#             "last_extracted_at",
#             "created_at",
#         )
#
#         db_table = "dairyapp_origin"
#
#
#     STATUS_CHOICES = [
#         ("a", "actual"),
#         ("f", "frozen"),
#         # ('j', 'job'),
#     ]
#     created_at = models.DateTimeField(auto_now_add=True)
#     last_extracted_at = models.DateTimeField(null=True)
#     name = models.CharField(max_length=30, unique=True)
#     status = models.CharField(
#         max_length=1, default="a", null=False, choices=STATUS_CHOICES
#     )
#     origin = models.CharField(max_length=2048, null=True, blank=True)
