from django.urls import path
from .views import (
    TaskCreateUpdateView,
    TaskListView,
    TaskDeleteView,
    ProjectDetailView,
    ProjectDeleteView,
    ProjectCreateView,
    ProjectUpdateView,
    ApproveTaskView,
    RevokeApprovalView,
    PendingTasksView
    
)

urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('create/', TaskCreateUpdateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', TaskCreateUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),
    path('projects/create/', ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/update/', ProjectUpdateView.as_view(), name='project_update'),
    path('approve/<int:task_id>/', ApproveTaskView.as_view(), name='approve_task'),
    path('revoke/<int:task_id>/', RevokeApprovalView.as_view(), name='revoke_approval'),
    path('tasks/pending/', PendingTasksView.as_view(), name='pending-tasks')
]


