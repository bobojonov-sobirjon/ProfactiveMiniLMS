from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import timedelta
from apps.accounts.models import CustomUser


class Categories(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True, verbose_name="Иконка категории")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Родительская категория")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "01. Категории"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_total_courses_count(self):
        """Get total count of courses in this category and all its subcategories"""
        # Get all subcategories recursively
        def get_all_subcategories(category):
            subcategories = Categories.objects.filter(parent=category)
            all_subcategories = list(subcategories)
            for subcategory in subcategories:
                all_subcategories.extend(get_all_subcategories(subcategory))
            return all_subcategories
        
        # Get all categories (current + all subcategories)
        all_categories = [self] + get_all_subcategories(self)
        
        # Count courses in all these categories
        return Courses.objects.filter(category__in=all_categories).count()


class MainCategory(Categories):
    """Proxy model for main categories only"""
    class Meta:
        proxy = True
        verbose_name = "Основная категория"
        verbose_name_plural = "01. Основные категории"


class SubCategory(Categories):
    """Proxy model for sub categories only"""
    class Meta:
        proxy = True
        verbose_name = "Подкатегория"
        verbose_name_plural = "02. Подкатегории"


class Courses(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание курса")
    image = models.ImageField(upload_to='courses/', verbose_name="Изображение курса")
    author = models.CharField(max_length=100, verbose_name="Автор курса")
    is_popular = models.BooleanField(default=False, verbose_name="Популярный курс")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, verbose_name="Категория")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "03. Курсы"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CourseChapter(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="Курс")
    title = models.CharField(max_length=200, verbose_name="Название главы")
    description = models.TextField(blank=True, null=True, verbose_name="Описание главы")
    is_activate = models.BooleanField(default=True, verbose_name="Активна")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Глава курса"
        verbose_name_plural = "04. Главы курсов"
        ordering = ['order']

    def __str__(self):
        return f"{self.course.name} - {self.title}"

    def get_total_duration(self):
        """Get total duration of all materials in this chapter"""
        total_seconds = sum(
            material.video_time.total_seconds() 
            for material in self.coursechaptervideo_set.filter(is_activate=True)
        )
        return total_seconds


class CourseChapterVideo(models.Model):
    chapter = models.ForeignKey(CourseChapter, on_delete=models.CASCADE, verbose_name="Глава")
    title = models.CharField(max_length=200, verbose_name="Название материала")
    description = models.TextField(blank=True, null=True, verbose_name="Описание материала")
    video_file = models.FileField(upload_to='course_videos/', verbose_name="Видео файл")
    video_time = models.DurationField(default=timedelta(hours=0, minutes=0), verbose_name="Длительность видео")
    is_activate = models.BooleanField(default=True, verbose_name="Активен")
    is_free = models.BooleanField(default=False, verbose_name="Бесплатный материал")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Видео главы"
        verbose_name_plural = "05. Видео глав"
        ordering = ['order']

    def __str__(self):
        return f"{self.chapter.title} - {self.title}"

    def get_file_url(self):
        """Get the video file URL if available"""
        if self.video_file:
            return self.video_file.url
        return None


class CourseChapterMaterials(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('document', 'Документ'),
        ('image', 'Изображение'),
    ]
    
    chapter = models.ForeignKey(CourseChapter, on_delete=models.CASCADE, verbose_name="Глава")
    title = models.CharField(max_length=200, verbose_name="Название материала")
    description = models.TextField(blank=True, null=True, verbose_name="Описание материала")
    material_type = models.CharField(
        max_length=20, 
        choices=MATERIAL_TYPE_CHOICES, 
        default='document',
        verbose_name="Тип материала"
    )
    image_file = models.ImageField(
        upload_to='course_materials/images/', 
        blank=True, 
        null=True, 
        verbose_name="Изображение"
    )
    document_file = models.FileField(
        upload_to='course_materials/documents/', 
        blank=True, 
        null=True, 
        verbose_name="Документ"
    )
    is_activate = models.BooleanField(default=True, verbose_name="Активен")
    is_free = models.BooleanField(default=False, verbose_name="Бесплатный материал")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Материал главы"
        verbose_name_plural = "06. Материалы глав"
        ordering = ['order']

    def __str__(self):
        return f"{self.chapter.title} - {self.title}"

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


class CourseReview(models.Model):
    """Course review model for user comments"""
    RATING_CHOICES = [
        (1, '1 звезда'),
        (2, '2 звезды'),
        (3, '3 звезды'),
        (4, '4 звезды'),
        (5, '5 звезд'),
    ]
    
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="Курс")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    comment = models.TextField(verbose_name="Комментарий")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, verbose_name="Рейтинг")
    is_active = models.BooleanField(default=False, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Отзыв о курсе"
        verbose_name_plural = "07. Отзывы о курсах"
        ordering = ['-created_at']
        unique_together = ['course', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.course.name} - {self.first_name} {self.last_name}"


class CourseQuiz(models.Model):
    """Quiz model for courses"""
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="Курс")
    title = models.CharField(max_length=200, verbose_name="Название теста")
    description = models.TextField(blank=True, null=True, verbose_name="Описание теста")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    passing_score = models.PositiveIntegerField(default=70, verbose_name="Проходной балл (%)")
    time_limit = models.PositiveIntegerField(default=30, verbose_name="Время на прохождение (минуты)")
    questions_count = models.PositiveIntegerField(default=10, verbose_name="Количество вопросов")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Тест курса"
        verbose_name_plural = "08. Тесты курсов"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.name} - {self.title}"

    def get_random_questions(self, count=None):
        """Get random questions for the quiz"""
        if count is None:
            count = self.questions_count
        return self.quizquestion_set.filter(is_active=True).order_by('?')[:count]


class QuizQuestion(models.Model):
    """Quiz question model"""
    quiz = models.ForeignKey(CourseQuiz, on_delete=models.CASCADE, verbose_name="Тест")
    question_text = models.TextField(verbose_name="Текст вопроса")
    option_a = models.CharField(max_length=500, verbose_name="Вариант A")
    option_b = models.CharField(max_length=500, verbose_name="Вариант B")
    option_c = models.CharField(max_length=500, verbose_name="Вариант C")
    correct_answer = models.CharField(
        max_length=1, 
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C')],
        verbose_name="Правильный ответ"
    )
    explanation = models.TextField(blank=True, null=True, verbose_name="Объяснение")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Вопрос теста"
        verbose_name_plural = "09. Вопросы тестов"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quiz.title} - {self.question_text[:50]}..."


class QuizAttempt(models.Model):
    """Quiz attempt model to track user attempts"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    quiz = models.ForeignKey(CourseQuiz, on_delete=models.CASCADE, verbose_name="Тест")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Время начала")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Время завершения")
    score = models.PositiveIntegerField(default=0, verbose_name="Балл")
    percentage = models.FloatField(default=0.0, verbose_name="Процент")
    is_passed = models.BooleanField(default=False, verbose_name="Пройден")
    is_completed = models.BooleanField(default=False, verbose_name="Завершен")
    answers = models.JSONField(default=dict, verbose_name="Ответы пользователя")
    time_taken = models.PositiveIntegerField(default=0, verbose_name="Время прохождения (секунды)")

    class Meta:
        verbose_name = "Попытка прохождения теста"
        verbose_name_plural = "10. Попытки прохождения тестов"
        ordering = ['-started_at']
        # Removed unique_together to allow multiple attempts

    def __str__(self):
        return f"{self.user.email} - {self.quiz.title} - {self.percentage}%"

    def calculate_score(self):
        """Calculate score based on answers"""
        if not self.answers:
            return 0, 0.0
        
        correct_answers = 0
        total_questions = len(self.answers)
        
        for question_id, user_answer in self.answers.items():
            try:
                question = QuizQuestion.objects.get(id=question_id)
                if user_answer == question.correct_answer:
                    correct_answers += 1
            except QuizQuestion.DoesNotExist:
                continue
        
        self.score = correct_answers
        self.percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        self.is_passed = self.percentage >= self.quiz.passing_score
        self.save()
        
        return self.score, self.percentage


class QuizCertificate(models.Model):
    """Certificate model for passed quizzes"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    quiz = models.ForeignKey(CourseQuiz, on_delete=models.CASCADE, verbose_name="Тест")
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, verbose_name="Попытка")
    certificate_number = models.CharField(max_length=50, unique=True, verbose_name="Номер сертификата")
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата выдачи")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Сертификат теста"
        verbose_name_plural = "11. Сертификаты тестов"
        ordering = ['-issued_at']
        unique_together = ['user', 'quiz']  # One certificate per user per quiz

    def __str__(self):
        return f"{self.user.email} - {self.quiz.title} - {self.certificate_number}"

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            import uuid
            self.certificate_number = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

