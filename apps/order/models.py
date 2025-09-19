from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from apps.accounts.models import CustomUser
from apps.courses.models import Courses, CourseChapter, CourseChapterVideo, CourseChapterMaterials


class CourseOrder(models.Model):
    """Model for course orders"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, blank=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="Курс")
    sender = models.EmailField(verbose_name="Email отправителя", null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    is_active = models.BooleanField(default=True, verbose_name="Активный заказ")
    is_completed = models.BooleanField(default=False, verbose_name="Заказ выполнен")
    notes = models.TextField(blank=True, null=True, verbose_name="Примечания")
    
    class Meta:
        verbose_name = "Заказ курса"
        verbose_name_plural = "1. Заказы курсов"
        ordering = ['-order_date']
        unique_together = ['sender', 'course']  # One order per email per course
    
    def __str__(self):
        user_email = self.user.email if self.user else self.sender
        return f"{user_email} - {self.course.name}"
    
    def activate_access(self):
        """Activate access for all course content"""
        self.is_active = True
        self.save()
        
        # Update all related content
        self.coursechapterforordereduser_set.update(is_accessible=True)
        self.coursevideoforordereduser_set.update(is_accessible=True)
        self.coursematerialforordereduser_set.update(is_accessible=True)
        
        print(f"Activated access for order {self.id} - all content is now accessible")


class CourseChapterForOrderedUser(models.Model):
    """Model for course chapters available to ordered users - with copied fields"""
    order = models.ForeignKey(CourseOrder, on_delete=models.CASCADE, verbose_name="Заказ")
    
    # Copied fields from CourseChapter
    title = models.CharField(max_length=200, verbose_name="Название главы")
    description = models.TextField(blank=True, null=True, verbose_name="Описание главы")
    is_activate = models.BooleanField(default=True, verbose_name="Активна")
    chapter_order = models.PositiveIntegerField(default=0, verbose_name="Порядок главы")
    
    # Access control
    is_accessible = models.BooleanField(default=True, verbose_name="Доступна")
    access_granted_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата предоставления доступа")
    
    class Meta:
        verbose_name = "Глава для заказанного пользователя"
        verbose_name_plural = "2. Главы для заказанных пользователей"
        ordering = ['chapter_order']
        unique_together = ['order', 'title', 'chapter_order']  # One record per order per chapter title and order
    
    def __str__(self):
        user_email = self.order.user.email if self.order.user else self.order.sender
        return f"{user_email} - {self.title}"


class CourseVideoForOrderedUser(models.Model):
    """Model for course videos available to ordered users - with copied fields"""
    order = models.ForeignKey(CourseOrder, on_delete=models.CASCADE, verbose_name="Заказ")
    chapter = models.ForeignKey(CourseChapterForOrderedUser, on_delete=models.CASCADE, verbose_name="Глава", null=True, blank=True)
    
    # Copied fields from CourseChapterVideo
    title = models.CharField(max_length=200, verbose_name="Название видео")
    description = models.TextField(blank=True, null=True, verbose_name="Описание видео")
    video_file = models.FileField(upload_to='course_videos/ordered/', verbose_name="Видео файл")
    video_time = models.DurationField(default=timedelta(hours=0, minutes=0), verbose_name="Длительность видео")
    is_activate = models.BooleanField(default=True, verbose_name="Активен")
    is_free = models.BooleanField(default=False, verbose_name="Бесплатный материал")
    video_order = models.PositiveIntegerField(default=0, verbose_name="Порядок видео")
    
    # Access control
    is_accessible = models.BooleanField(default=True, verbose_name="Доступно")
    access_granted_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата предоставления доступа")
    
    class Meta:
        verbose_name = "Видео для заказанного пользователя"
        verbose_name_plural = "3. Видео для заказанных пользователей"
        ordering = ['video_order']
        unique_together = ['order', 'title', 'video_order']  # One record per order per video title and order
    
    def __str__(self):
        user_email = self.order.user.email if self.order.user else self.order.sender
        return f"{user_email} - {self.title}"
    
    def get_file_url(self):
        """Get the video file URL if available"""
        if self.video_file:
            return self.video_file.url
        return None


class CourseMaterialForOrderedUser(models.Model):
    """Model for course materials available to ordered users - with copied fields"""
    MATERIAL_TYPE_CHOICES = [
        ('document', 'Документ'),
        ('image', 'Изображение'),
    ]
    
    order = models.ForeignKey(CourseOrder, on_delete=models.CASCADE, verbose_name="Заказ")
    chapter = models.ForeignKey(CourseChapterForOrderedUser, on_delete=models.CASCADE, verbose_name="Глава", null=True, blank=True)
    
    # Copied fields from CourseChapterMaterials
    title = models.CharField(max_length=200, verbose_name="Название материала")
    description = models.TextField(blank=True, null=True, verbose_name="Описание материала")
    material_type = models.CharField(
        max_length=20, 
        choices=MATERIAL_TYPE_CHOICES, 
        default='document',
        verbose_name="Тип материала"
    )
    image_file = models.ImageField(
        upload_to='course_materials/ordered/images/', 
        blank=True, 
        null=True, 
        verbose_name="Изображение"
    )
    document_file = models.FileField(
        upload_to='course_materials/ordered/documents/', 
        blank=True, 
        null=True, 
        verbose_name="Документ"
    )
    is_activate = models.BooleanField(default=True, verbose_name="Активен")
    is_free = models.BooleanField(default=False, verbose_name="Бесплатный материал")
    material_order = models.PositiveIntegerField(default=0, verbose_name="Порядок материала")
    
    # Access control
    is_accessible = models.BooleanField(default=True, verbose_name="Доступен")
    access_granted_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата предоставления доступа")
    
    class Meta:
        verbose_name = "Материал для заказанного пользователя"
        verbose_name_plural = "4. Материалы для заказанных пользователей"
        ordering = ['material_order']
        unique_together = ['order', 'title', 'material_order']  # One record per order per material title and order
    
    def __str__(self):
        user_email = self.order.user.email if self.order.user else self.order.sender
        return f"{user_email} - {self.title}"
    
    def clean(self):
        """Validate that appropriate fields are filled based on material type"""
        super().clean()
        
        if self.material_type == 'document':
            if not self.document_file:
                raise ValidationError({
                    'document_file': 'Документ обязателен для типа материала "Документ"'
                })
            if self.image_file:
                raise ValidationError({
                    'image_file': 'Изображение не должно быть заполнено для типа материала "Документ"'
                })
        elif self.material_type == 'image':
            if not self.image_file:
                raise ValidationError({
                    'image_file': 'Изображение обязательно для типа материала "Изображение"'
                })
            if self.document_file:
                raise ValidationError({
                    'document_file': 'Документ не должен быть заполнен для типа материала "Изображение"'
                })

    def get_file_url(self):
        """Get the appropriate file URL based on material type"""
        if self.material_type == 'document' and self.document_file:
            return self.document_file.url
        elif self.material_type == 'image' and self.image_file:
            return self.image_file.url
        return None


class UserVideoProgress(models.Model):
    """Model to track user's video watching progress"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    video = models.ForeignKey(CourseVideoForOrderedUser, on_delete=models.CASCADE, verbose_name="Видео")
    is_watched = models.BooleanField(default=False, verbose_name="Просмотрено")
    watched_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата просмотра")
    watch_duration = models.DurationField(default=timedelta(seconds=0), verbose_name="Время просмотра")
    
    class Meta:
        verbose_name = "Прогресс просмотра видео"
        verbose_name_plural = "5. Прогресс просмотра видео"
        unique_together = ['user', 'video']  # One progress record per user per video
    
    def __str__(self):
        return f"{self.user.email} - {self.video.title} - {'Просмотрено' if self.is_watched else 'Не просмотрено'}"