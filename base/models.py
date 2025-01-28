from django.db import models
from account.models import UserProfile


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="created_projects"
    )

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
        ("Pending Approval", "Pending Approval"),
    ]

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateTimeField()
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="Medium"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name="assigned_tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="created_tasks"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TaskConfigurations(models.Model):
    config_name = models.CharField(max_length=256)
    config_value = models.CharField(max_length=64)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="task_configuration"
    )

    def _str_(self):
        return self.config_name
