from django.core.exceptions import ValidationError
from django.db import models
from datetime import datetime

from django.http import HttpRequest


class Day(models.Model):
    created_at = models.DateTimeField()
    content = models.TextField(null=True, blank=True)


class Quest(models.Model):
    class Meta:
        ordering = "completed_at", "created_at"
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # Hold description
    theme_description = models.CharField(max_length=500, null=True, blank=True)
    # Rooms
    total_tasks = models.SmallIntegerField(default=0)
    # Completed Rooms
    total_completed_tasks = models.SmallIntegerField(default=0)
    # deaths
    errors = models.JSONField(default=list)
    complete_description = models.TextField(max_length=1000, null=True, blank=True)
    origin = models.ForeignKey("Origin", on_delete=models.SET_NULL, null=True)

    def clean(self):
        super().clean()
        if self.total_tasks < self.total_completed_tasks:
            raise ValidationError

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.clean()
        if not self.completed_at and self.complete_description:
            self.completed_at = datetime.now()
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
