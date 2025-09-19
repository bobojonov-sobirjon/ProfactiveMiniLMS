from django.core.management.base import BaseCommand
from apps.order.models import CourseOrder


class Command(BaseCommand):
    help = 'Test signal by updating an order'

    def handle(self, *args, **options):
        # Get the first order
        order = CourseOrder.objects.first()
        if order:
            self.stdout.write(f'Found order: {order}')
            self.stdout.write(f'Current is_active: {order.is_active}')
            
            # Update is_active to True
            order.is_active = True
            order.save()
            
            self.stdout.write(f'Updated is_active to: {order.is_active}')
        else:
            self.stdout.write('No orders found')
