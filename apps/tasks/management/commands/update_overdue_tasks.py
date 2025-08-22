from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tasks.repository import TaskRepository


class Command(BaseCommand):
    help = 'Update overdue tasks from active to failed status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all overdue tasks',
        )

    def handle(self, *args, **options):
        repository = TaskRepository()
        
        if options['force']:
            updated_count = repository.force_update_all_overdue_tasks()
            self.stdout.write(
                self.style.SUCCESS(f'Force updated {updated_count} overdue tasks')
            )
        else:
            updated_count = repository.ensure_overdue_tasks_are_failed()
            self.stdout.write(
                self.style.SUCCESS(f'Updated {updated_count} overdue tasks to failed status')
            )
        
        # Show current statistics
        active_count = repository.get_active_tasks().count()
        completed_count = repository.get_completed_tasks().count()
        failed_count = repository.get_failed_tasks().count()
        
        self.stdout.write(
            self.style.WARNING(
                f'Current task status: Active: {active_count}, Completed: {completed_count}, Failed: {failed_count}'
            )
        )
