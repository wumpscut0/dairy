from logging import getLogger

from django.db.transaction import atomic
from django.utils.timezone import now
from rest_framework.fields import IntegerField
from rest_framework.serializers import ModelSerializer

from .models import Quest, Error, Problem, Knowledge, Task, TYPES, Origin

logger = getLogger("stdout")


class ErrorModelSerializer(ModelSerializer):
    class Meta:
        model = Error
        fields = "text", "type"


class ProblemModelSerializer(ModelSerializer):
    class Meta:
        model = Problem
        fields = "text", "type"


class KnowledgeModelSerializer(ModelSerializer):
    class Meta:
        model = Knowledge
        fields = "text", "type"


class TaskCreateModelSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = "text", "type", "status"


class TaskUpdateModelSerializer(ModelSerializer):
    id = IntegerField(read_only=False)

    class Meta:
        model = Task
        fields = "id", "text", "type", "status"


class QuestCreateModelSerializer(ModelSerializer):
    tasks = TaskCreateModelSerializer(many=True)

    class Meta:
        model = Quest
        fields = "theme", "tasks", "origin"

    def create(self, validated_data):
        logger.debug(
            f"Class: {self.__class__.__name__}\nMethod: {self.create.__name__}\nvalidation data: {validated_data}"
        )
        with atomic():
            quest = Quest.objects.create(
                theme=validated_data["theme"], origin=validated_data["origin"]
            )
            data_to_create = []
            for data in validated_data["tasks"]:
                data["quest_id"] = quest.pk
                data_to_create.append(Task(**data))
            Task.objects.bulk_create(data_to_create)
            Origin.objects.filter(pk=validated_data["origin"]).update(
                last_extracted_at=now()
            ).save()
            return quest


class QuestEditModelSerializer(ModelSerializer):
    item_map = (
        (Error, "errors"),
        (Problem, "problems"),
        (Knowledge, "knowledge"),
    )
    tasks = TaskUpdateModelSerializer(many=True)
    errors = ErrorModelSerializer(many=True)
    problems = ProblemModelSerializer(many=True)
    knowledge = KnowledgeModelSerializer(many=True)

    class Meta:
        model = Quest
        fields = "tasks", "errors", "problems", "knowledge"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["types"] = TYPES
        return data

    def update(self, instance, validated_data):
        logger.debug(
            f"Class: {self.__class__.__name__}\nMethod: {self.update.__name__}\nInstance: {instance.__class__.__name__}\nvalidation data: {validated_data}"
        )
        with atomic():
            for item_class, key in self.item_map:
                item_class.objects.filter(quest=instance).delete()
                data_to_create = []
                for data in validated_data[key]:
                    data["quest"] = instance
                    data_to_create.append(item_class(**data))
                item_class.objects.bulk_create(data_to_create)
            done = True
            for task in validated_data["tasks"]:
                if not task["status"]:
                    done = False
                Task.objects.filter(pk=task["id"]).update(status=task["status"])
            instance.last_update = now()
            if not instance.completed_at and done:
                instance.completed_at = now()
            instance.save()
        return instance
