from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    patronymic = models.CharField(max_length=150, verbose_name='Отчество', blank=True)
    is_deleted = models.BooleanField(default=False, verbose_name='Удален')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
    is_superuser = models.BooleanField(default=False, verbose_name='Суперпользователь')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.email})"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()


class CourseEnrollment(models.Model):
    """Model for course enrollments"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    course = models.ForeignKey('courses.Courses', on_delete=models.CASCADE, verbose_name="Курс")
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата записи")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    
    class Meta:
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курсы"
        unique_together = ['user', 'course']  # One enrollment per user per course
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.name}"