from django.contrib import admin
from .models import Project, Task, TaskConfigurations


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "created_by", "created_at")
    list_filter = ("created_at", "created_by")
    search_fields = ("name", "description")
    ordering = ("-created_at",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "priority",
        "status",
        "project",
        "assigned_to",
        "due_date",
        "created_at",
    )
    list_filter = ("priority", "status", "project", "due_date")
    search_fields = ("title", "description", "assigned_to__username", "project__name")
    ordering = ("-due_date",)
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "description",
                    "priority",
                    "status",
                    "project",
                    "created_by",
                )
            },
        ),
        ("Assignment", {"fields": ("assigned_to", "due_date")}),
    )


admin.site.register(TaskConfigurations)
