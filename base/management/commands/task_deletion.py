from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from base.models import Task

class Command(BaseCommand):
    help = 'Deletes completed tasks older than a configurable period'

    def handle(self, *args, **kwargs):
        # Set the deletion period (configurable in settings)
        from django.conf import settings
        days = getattr(settings, 'TASK_DELETION_DAYS', 2)
        deletion_time = now() - timedelta(days=days)

        # Delete tasks that meet the criteria
        tasks_deleted, _ = Task.objects.filter(
            status='Completed',
            updated_at__lt=deletion_time
        ).delete()

        self.stdout.write(f'{tasks_deleted} tasks deleted successfully.')
