from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task, Project
from .serializers import TaskSerializer, ProjectSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .permissions import IsAdmin
from .task import save_task_to_db
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache


class TaskCreateUpdateView(APIView):
    """
    Admin: Full access
    Manager: Can create and update tasks, mark tasks as completed
    User: Can create and update assigned tasks, and update status to in-progress
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ["Admin", "Manager", "User"]:
            return Response(
                {"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaskSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            task = serializer.save()  # `created_by` is automatically added here
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if request.user.role == "User" and task.assigned_to != request.user:
            return Response(
                {"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
            )
        elif request.user.role == "Manager" and task.status == "Completed":
            return Response(
                {"error": "Managers cannot update completed tasks."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskSerializer(
            task, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            task = serializer.save()
            return Response(
                {
                    "message": "Task updated successfully",
                    "task": TaskSerializer(task).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.select_related("project", "assigned_to").all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["priority", "status", "due_date"]
    ordering_fields = ["priority", "due_date"]

    def get_queryset(self):
        if self.request.user.role == "User":
            return Task.objects.filter(assigned_to=self.request.user)
        return super().get_queryset()


class ProjectDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.prefetch_related("tasks").annotate(
        total_tasks=Count("tasks"),
        completed_tasks=Count("tasks", filter=Q(tasks__status="Completed")),
    )
    serializer_class = ProjectSerializer


class TaskDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)

        # Check permissions based on role
        if request.user.role == "User":
            return Response(
                {"error": "Users cannot delete tasks."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if request.user.role == "Manager" and task.status == "Completed":
            return Response(
                {"error": "Managers cannot delete completed tasks."},
                status=status.HTTP_403_FORBIDDEN,
            )

        task.delete()
        return Response(
            {"message": "Task deleted successfully."}, status=status.HTTP_204_NO_CONTENT
        )


class ProjectDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        project.delete()
        return Response(
            {"message": "Project and its tasks deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class ProjectCreateView(generics.CreateAPIView):
    permission_classes = [IsAdmin]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProjectUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def put(self, request, *args, **kwargs):
        # project = self.get_object()
        if request.user.role == "Manager":
            return Response(
                {"error": "Managers cannot update projects."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().update(request, *args, **kwargs)


# class ApproveTaskView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, task_id):
#         user = request.user

#         # Check user's role (optional, modify based on your role structure)
#         if user.role != 'Manager':  # Assuming user role is stored in a field
#             return Response({'error': 'You do not have permission to approve tasks.'}, status=403)

#         # Get the task object
#         task = get_object_or_404(Task, id=task_id)

#         if task.status != 'Pending Approval':
#             return Response({'error': 'This task cannot be approved as it is not pending approval.'}, status=400)

#         # Temporarily save task data in Redis
#         task_data = {
#             'title': task.title,
#             'description': task.description,
#             'status': task.status,
#             'created_at': str(task.created_at)
#         }
#         cache.set(f'task:{task_id}', task_data, timeout=300)  # Store in Redis for 5 minutes

#         # Update task status to approved
#         task.status = 'Approved'
#         task.save()

#         # Schedule the Celery task to save the task in the main database after 5 minutes
#         save_task_to_db.apply_async((task.id,), countdown=300)  # 5-minute delay

#         return Response({'message': 'Task has been approved and will be saved in 5 minutes.'}, status=200)


class ApproveTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        user = request.user
        if user.role != "Manager":
            return Response(
                {"error": "You do not have permission to approve tasks."}, status=403
            )

        task = get_object_or_404(Task, id=task_id)

        if task.status != "Pending Approval":
            return Response(
                {
                    "error": "This task cannot be approved as it is not pending approval."
                },
                status=400,
            )
        task_data = {
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "created_at": str(task.created_at),
        }
        cache.set(f"task:{task_id}", task_data, timeout=300)
        save_task_to_db.apply_async((task.id,), countdown=300)

        return Response(
            {"message": "Task has been approved and will be saved in 5 minutes."},
            status=200,
        )


class RevokeApprovalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, task_id):
        task = get_object_or_404(Task, id=task_id)

        if task.status != "Approved":
            return Response(
                {"error": "This task cannot be revoked as it is not approved."},
                status=400,
            )
        task.status = "Pending Approval"
        task.save()
        cache_key = f"task:{task_id}"
        if cache.get(cache_key):
            cache.delete(cache_key)

        return Response(
            {
                "message": "Task approval has been revoked and will not be saved to the database."
            },
            status=200,
        )


class PendingTasksView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role != "Manager":
            return Task.objects.none()
        return Task.objects.filter(status="Pending Approval")
