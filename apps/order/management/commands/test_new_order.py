from django.core.management.base import BaseCommand
from apps.order.models import CourseOrder
from apps.accounts.models import CustomUser
from apps.courses.models import Courses


class Command(BaseCommand):
    help = 'Test signal with a new order'

    def handle(self, *args, **options):
        # Get a user and course
        user = CustomUser.objects.first()
        course = Courses.objects.first()
        
        if user and course:
            # Create a new order with is_active=False
            order = CourseOrder.objects.create(
                user=user,
                course=course,
                is_active=False
            )
            self.stdout.write(f'Created order: {order}')
            self.stdout.write(f'Initial is_active: {order.is_active}')
            
            # Now activate it
            order.is_active = True
            order.save()
            
            self.stdout.write(f'Activated order: {order.is_active}')
        else:
            self.stdout.write('No user or course found')
