from django.db import models
from django.utils import timezone
import secrets
import string

class FAQ(models.Model):
    """FAQ (Frequently Asked Questions) model"""
    question = models.CharField(
        max_length=500,
        verbose_name="Вопрос",
        help_text="FAQ вопрос"
    )
    answer = models.TextField(
        verbose_name="Ответ",
        help_text="FAQ ответ"
    )
    category = models.CharField(
        max_length=100,
        verbose_name="Категория",
        help_text="FAQ категория",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Активен ли FAQ"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
        help_text="Порядок отображения"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "1. FAQ"
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.question[:50] + "..." if len(self.question) > 50 else self.question


class AboutSection(models.Model):
    """About page sections model"""
    title = models.TextField(
        verbose_name="Заголовок",
        help_text="Заголовок секции (может содержать HTML теги)"
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Описание секции"
    )
    keywords = models.CharField(
        max_length=200,
        verbose_name="Ключевые слова",
        help_text="Слова которые будут выделены золотым цветом (через запятую)"
    )
    image = models.ImageField(
        upload_to='about/sections/',
        verbose_name="Изображение",
        help_text="Изображение для секции"
    )
    button_text = models.CharField(
        max_length=100,
        verbose_name="Текст кнопки",
        help_text="Текст кнопки (если есть)",
        blank=True,
        null=True
    )
    button_url = models.URLField(
        verbose_name="Ссылка кнопки",
        help_text="Ссылка кнопки",
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
        help_text="Порядок отображения"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Активна ли секция"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "О нас"
        verbose_name_plural = "2. О нас"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Секция {self.order}: {self.title[:50]}..."

    def get_highlighted_title(self):
        """Возвращает заголовок с выделенными ключевыми словами"""
        title = self.title
        if self.keywords:
            keywords = [kw.strip() for kw in self.keywords.split(',')]
            for keyword in keywords:
                if keyword in title:
                    title = title.replace(
                        keyword, 
                        f'<span class="text-gradient-display">{keyword}</span>'
                    )
        return title


class Blog(models.Model):
    """Blog model for blog posts"""
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок",
        help_text="Заголовок блога"
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Описание блога"
    )
    image = models.ImageField(
        upload_to='blog/',
        verbose_name="Изображение",
        help_text="Изображение для блога"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Активен ли блог"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Блог"
        verbose_name_plural = "3. Блоги"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ReferralRequest(models.Model):
    """Referral request model for referral program"""
    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя",
        help_text="Имя пользователя"
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
        help_text="Фамилия пользователя"
    )
    email = models.EmailField(
        verbose_name="Email",
        help_text="Email адрес пользователя"
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name="Номер телефона",
        help_text="Номер телефона пользователя"
    )
    promo_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Промокод",
        help_text="Уникальный промокод"
    )
    referral_link = models.URLField(
        verbose_name="Реферальная ссылка",
        help_text="Уникальная реферальная ссылка"
    )
    # Referral sender information
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Приглашен пользователем",
        help_text="Кто пригласил этого пользователя"
    )
    referred_by_name = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name="Имя пригласившего",
        help_text="Имя и фамилия того, кто пригласил"
    )
    referred_by_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email пригласившего",
        help_text="Email того, кто пригласил"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Активен ли промокод"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Реферальная заявка"
        verbose_name_plural = "5. Реферальные заявки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

    def save(self, *args, **kwargs):
        if not self.promo_code:
            self.promo_code = self.generate_promo_code()
        if not self.referral_link:
            self.referral_link = self.generate_referral_link()
        super().save(*args, **kwargs)

    def generate_promo_code(self):
        """Generate unique promo code"""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            if not ReferralRequest.objects.filter(promo_code=code).exists():
                return code

    def generate_referral_link(self):
        """Generate unique referral link"""
        from django.conf import settings
        return f"{settings.SITE_URL}/referral/{self.promo_code}/"


class Document(models.Model):
    """Document model for documentation page"""
    title = models.CharField(
        max_length=200,
        verbose_name="Название документа",
        help_text="Название документа"
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Описание документа",
        blank=True,
        null=True
    )
    file = models.FileField(
        upload_to='documents/',
        verbose_name="Файл",
        help_text="Файл документа"
    )
    file_type = models.CharField(
        max_length=10,
        verbose_name="Тип файла",
        help_text="Тип файла (PDF, DOC, etc.)",
        blank=True,
        null=True
    )
    file_size = models.PositiveIntegerField(
        verbose_name="Размер файла (байт)",
        help_text="Размер файла в байтах",
        blank=True,
        null=True
    )
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество скачиваний",
        help_text="Количество скачиваний файла"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Активен ли документ"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
        help_text="Порядок отображения"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "4. Документы"
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file:
            # Автоматически определяем тип файла
            file_extension = self.file.name.split('.')[-1].upper()
            self.file_type = file_extension
            
            # Получаем размер файла
            try:
                self.file_size = self.file.size
            except:
                pass
        super().save(*args, **kwargs)

    def get_file_size_display(self):
        """Возвращает размер файла в удобном формате"""
        if not self.file_size:
            return "Неизвестно"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"