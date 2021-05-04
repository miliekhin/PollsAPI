from django.core.management import BaseCommand, call_command
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Project installation'

    def handle(self, *args, **kwargs):
        call_command('makemigrations')
        call_command('migrate')
        call_command('flush', verbosity=0, interactive=False)
        call_command('createsuperuser', interactive=False, username='testadmin', email='testadmin@example.com')
        user = User.objects.get(username='testadmin')
        user.set_password('testadmin')
        user.save()

        self.stdout.write(self.style.SUCCESS('Проект был успешно настроен.'))
