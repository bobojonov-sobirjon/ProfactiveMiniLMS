from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
import secrets
import string

User = get_user_model()


@receiver(post_save, sender=User)
def send_user_credentials_email(sender, instance, created, **kwargs):
    """Send email with login credentials when a new user is created"""
    if created:
        # Get the password from the raw password (before hashing)
        # We need to get it from the admin form
        password = getattr(instance, '_raw_password', None)
        
        if not password:
            # If no password was provided, generate a random one
            password_length = 12
            characters = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(secrets.choice(characters) for _ in range(password_length))
            instance.set_password(password)
            instance.save()
        
        # Prepare email content in Russian
        subject = 'Ваши данные для входа в Profactive'
        
        message = f'''
Здравствуйте, {instance.first_name} {instance.last_name}!

Администратор создал для вас аккаунт в системе Profactive.

Ваши данные для входа:
Email: {instance.email}
Пароль: {password}

Теперь вы можете войти в систему и просматривать ваши курсы.

С уважением,
Команда Profactive
        '''
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[instance.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending user credentials email: {e}")
