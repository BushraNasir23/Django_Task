from rest_framework import serializers
from .models import Task, Project
from django.utils.timezone import now


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["created_by"]

    def create(self, validated_data):
        created_by = self.context["request"].user
        return Task.objects.create(created_by=created_by, **validated_data)

    def validate_due_date(self, value):
        if value <= now():
            raise serializers.ValidationError("The due date must be in the future.")
        return value

    def validate_project(self, value):
        if not Project.objects.filter(pk=value.id).exists():
            raise serializers.ValidationError(
                f'Invalid pk "{value.id}" - object does not exist.'
            )
        return value


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
