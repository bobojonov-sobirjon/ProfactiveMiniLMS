from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email sending'

    def handle(self, *args, **options):
        try:
            result = send_mail(
                subject='Test Email',
                message='This is a test email from Django.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['sobirbobojonov2000@gmail.com'],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(f'Email sent successfully: {result}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error sending email: {e}')
            )
