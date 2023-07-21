from rest_framework import serializers
from .models import Task, SubTask
from django.utils import timezone


class SubTaskSerializer(serializers.ModelSerializer):
    """하위업무(SubTask) 시리얼라이저

    SubTask 정보 시리얼라이저
    """

    class Meta:
        model = SubTask
        fields = (
            "id",
            "team",
            "is_complete",
            "completed_date",
            "created_at",
            "modified_at",
        )

    def update(self, instance, validated_data):
        instance.modified_at = timezone.now()
        instance.save()
        return super().update(instance, validated_data)


class TaskSerializer(serializers.ModelSerializer):
    """업무(Task) 시리얼라이저

    Task 정보 시리얼라이저
    """

    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "create_user",
            "team",
            "title",
            "content",
            "is_complete",
            "completed_date",
            "created_at",
            "modified_at",
            "subtasks",
        )

    def update(self, instance, validated_data):
        instance.modified_at = timezone.now()
        instance.save()
        return super().update(instance, validated_data)
