from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Reset fake migrations for a given app'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='The app name to reset migrations for')

    def handle(self, *args, **kwargs):
        app_name = kwargs['app_name']
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_migrations WHERE app = %s", [app_name])
        self.stdout.write(self.style.SUCCESS(f"Successfully reset migrations for app '{app_name}'"))
