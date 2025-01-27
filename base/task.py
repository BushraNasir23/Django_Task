from django_celery_beat.models import PeriodicTask, IntervalSchedule
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from celery import shared_task
from django.core.cache import cache
from .models import Task ,TaskConfigurations
from .management.commands.task_deletion import Command
import datetime

# @shared_task
# def delete_old_completed_tasks():
#     # This will call the management command as a Celery task
#     command = Command()
#     command.handle()
    

# tasks.py
@shared_task
def delete_old_completed_tasks():
    # This will call the management command as a Celery task
    # Time should be in number of days.
    deletion_time = TaskConfigurations.objects.filter(config_name="task_expiry").last()
    deletion_time = int(deletion_time) if deletion_time else 2
    deletion_time = datetime.now() - timedelta(days=deletion_time)
    Task.objects.filter(created_at__lte=deletion_time, status="Completed").delete()



@shared_task
def save_task_to_db(task_id):
    # Retrieve the task from Redis
    task_data = cache.get(f'task:{task_id}')
    if not task_data:
        return f"Task {task_id} not found or approval revoked."

    # Get the actual task object from the database
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return f"Task {task_id} not found in the database."

    # Ensure the task is still approved
    if task.status == 'Pending Approval':
        task.status = 'Approved'
        task.save()
        # Remove the task from Redis after saving
        cache.delete(f'task:{task_id}')
        return f"Task {task_id} approved and saved to the database."
    else:
        task.delete()  # Optionally delete the task if status is not pending
        cache.delete(f'task:{task_id}')
        return f"Task {task_id} was not approved and has been discarded."



