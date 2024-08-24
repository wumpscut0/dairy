from json import load
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models

from django.db.models import TextField
from django.utils.timezone import now

TYPES_PATH = Path("types.json").resolve()
with open(TYPES_PATH) as file:
	TYPES = load(file)
	DONE_TYPES = list(TYPES["done"])
	ERROR_TYPES = list(TYPES["errors"])
	PROBLEM_TYPES = list(TYPES["problems"])
	KNOWLEDGE_TYPES = list(TYPES["knowledge"])

def done_types_validator(value):
	if value and value not in DONE_TYPES:
		raise ValidationError("Wrong type")

def errors_types_validator(value):
	if value and value not in ERROR_TYPES:
		raise ValidationError("Wrong type")

def problem_types_validator(value):
	if value and value not in PROBLEM_TYPES:
		raise ValidationError("Wrong type")

def knowledge_types_validator(value):
	if value and value not in KNOWLEDGE_TYPES:
		raise ValidationError("Wrong type")

class Day(models.Model):
	created_at = models.DateTimeField()
	content = models.TextField(null=True, blank=True)

class Done(models.Model):
	type = models.CharField(max_length=50, validators=(done_types_validator,), null=True, blank=True)
	text = TextField(max_length=1000, null=True, blank=True)
	quest = models.ForeignKey("Quest", on_delete=models.CASCADE, related_name="done")

class Error(models.Model):
	type = models.CharField(max_length=50, validators=(errors_types_validator,), null=True, blank=True)
	text = TextField(max_length=1000, null=True, blank=True)
	quest = models.ForeignKey("Quest", on_delete=models.CASCADE, related_name="errors")

class Problem(models.Model):
	type = models.CharField(max_length=50, validators=(problem_types_validator,), null=True, blank=True)
	text = TextField(max_length=1000, null=True, blank=True)
	quest = models.ForeignKey("Quest", on_delete=models.CASCADE, related_name="problems")

class Knowledge(models.Model):
	type = models.CharField(max_length=50, validators=(knowledge_types_validator,), null=True, blank=True)
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
