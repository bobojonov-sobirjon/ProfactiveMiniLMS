from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import CourseOrder
from apps.accounts.models import CustomUser


@receiver(post_save, sender=CourseOrder)
def handle_course_order_activation(sender, instance, created, **kwargs):
    """Handle CourseOrder activation and assign user if sender email matches"""
    if not created and instance.is_active:
        # If order is activated and user is not assigned yet
        if not instance.user and instance.sender:
            try:
                # Find user by sender email
                user = CustomUser.objects.get(email=instance.sender)
                # Assign user to the order
                instance.user = user
                instance.save(update_fields=['user'])
                
                # Send email notification to user
                subject = f'Доступ к курсу "{instance.course.name}" активирован'
                
                message = f'''
Здравствуйте, {user.first_name} {user.last_name}!

Ваш доступ к курсу "{instance.course.name}" был активирован администратором.

Теперь вы можете:
- Просматривать все материалы курса
- Смотреть видеоуроки
- Скачивать дополнительные материалы
- Отслеживать свой прогресс

Для входа в систему используйте:
Email: {user.email}
Пароль: (ваш текущий пароль)

С уважением,
Команда Profactive
                '''
                
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error sending activation email: {e}")
                    
            except CustomUser.DoesNotExist:
                print(f"User with email {instance.sender} not found")
            except Exception as e:
                print(f"Error assigning user to order: {e}")
        
        # Always update access for all related content when order is activated
        try:
            from .models import CourseChapterForOrderedUser, CourseVideoForOrderedUser, CourseMaterialForOrderedUser
            
            # Update all related content to be accessible
            CourseChapterForOrderedUser.objects.filter(order=instance).update(is_accessible=True)
            CourseVideoForOrderedUser.objects.filter(order=instance).update(is_accessible=True)
            CourseMaterialForOrderedUser.objects.filter(order=instance).update(is_accessible=True)
            
            print(f"Updated access for order {instance.id} - all content is now accessible")
            
        except Exception as e:
            print(f"Error updating content access for order {instance.id}: {e}")