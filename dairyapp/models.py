from django.db import models
from datetime import datetime


class Quest(models.Model):
    class Meta:
        ordering = "completed_at", "created_at"
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    complete_description = models.TextField(max_length=1000, null=True, blank=True)
    origin = models.ForeignKey("Origin", on_delete=models.SET_NULL, null=True)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
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
