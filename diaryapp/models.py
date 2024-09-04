from logging import getLogger
from typing import Dict
from urllib.error import URLError
from urllib.request import urlopen

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now

logger = getLogger("stdout")



def calc_max_length(data: Dict):
    return len(max(data, key=lambda x: len(x)))


def reaper(pk: int):
    try:
        target = Target.objects.get(pk=pk)
        target.status = "failed"
        target.save()
    except Target.DoesNotExists:
        logger.error(f"With trying set `failed` flag for Target with pk {pk}, Target was not found")


def future_date(value):
    if value <= now():
        raise ValidationError("planned_datetime can`t be in the past")

class Note(models.Model):
    created_at = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    
    note = models.TextField(null=True, blank=True)


class Target(models.Model):
    statuses = {
        "process": "В процессе",
        "done": "Выполнено",
        "failed": "Провалено",
        "canceled": "Отменено"
    }
    types = {
        "ultimate": "UT",
        "story": "Сюжет",
        "additional": "Дополнение",
        "task": "Задача"
    }
    
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=calc_max_length(types), default="task", choices=types)
    
    over_at = models.DateTimeField(null=True)
    planned_datetime = models.DateTimeField(null=True, validators=(future_date,))
    status = models.CharField(max_length=calc_max_length(statuses), default="process", choices=statuses)
    group_priority = models.IntegerField(default=0, help_text="priority grouped by type")
    condition = models.TextField(max_length=255, help_text="user condition for determining the task status")
    description = models.TextField(max_length=1000, help_text="free textarea with any description")
    
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
    types = {
        "unknown": "Неизвестно",
        "0": "0",
        "some": "Некоторое",
        "volume": "Объёмное",
        "full": "Полное",
    }
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="books")
    
    author = models.CharField(max_length=30)
    name = models.CharField(max_length=15)
    file = models.FileField(upload_to="books", null=True)
    comprehension = models.CharField(max_length=calc_max_length(types), default="unknown", choices=types)
    
    class Meta:
        unique_together = ("author", "name")



class Area(models.Model):
    types = {
        "programming_language": "Язык программирования",
        "technology": "Технология",  # Инструмент управления технологией
        "science": "Наука",  # Область
        "paradigm": "Парадигма",
        "method": "Метод",
        "Framework": "Фреймворк",
        "library": "Библиотека",
        "language": "Язык",
        "other": "Другое",
    }
    grades = {
        "0": "0",
        "beginner": "Базовый",
        "middle": "Средний",
        "advanced": "Продвинутый"
    }
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="areas")

    name = models.CharField(max_length=20)
    type = models.CharField(max_length=calc_max_length(types), default="other", choices=types)
    grade = models.CharField(max_length=calc_max_length(grades), default="0", choices=grades)
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
