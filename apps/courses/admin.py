from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import (
    MainCategory, SubCategory, Courses, CourseChapter, CourseChapterVideo, CourseChapterMaterials, CourseReview,
    CourseQuiz, QuizQuestion, QuizAttempt, QuizCertificate)


class CourseChapterVideoInline(admin.TabularInline):
    model = CourseChapterVideo
    extra = 1
    fk_name = 'chapter'
    verbose_name = 'Видео материал'
    verbose_name_plural = 'Видео материалы'
    fields = ['title', 'description', 'video_file', 'video_time', 'is_activate', 'is_free']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    def formfield_for_duration_field(self, db_field, request, **kwargs):
        if db_field.name == 'video_time':
            kwargs['widget'] = forms.TextInput(attrs={'placeholder': 'HH:MM:SS (например: 01:30:00)'})
        return super().formfield_for_duration_field(db_field, request, **kwargs)


class CourseChapterMaterialsInline(admin.TabularInline):
    model = CourseChapterMaterials
    extra = 1
    fk_name = 'chapter'
    verbose_name = 'Материал главы'
    verbose_name_plural = 'Материалы глав'
    fields = ['title', 'description', 'material_type', 'image_file', 'document_file', 'is_activate', 'is_free']
    readonly_fields = ['created_at']
    
    class Media:
        js = ('admin/js/course_materials_admin.js',)
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        # Add JavaScript to each form in the formset
        if hasattr(formset.form, 'base_forms'):
            for form in formset.form.base_forms:
                if 'material_type' in form.fields:
                    form.fields['material_type'].widget.attrs.update({
                        'onchange': 'toggleFileFields()'
                    })
        
        return formset



@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_preview', 'created_at', 'subcategories_count']
    list_filter = ['created_at']
    search_fields = ['name']
    ordering = ['name']
    readonly_fields = ['created_at']
    fields = ['name', 'icon', 'created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent__isnull=True)

    def icon_preview(self, obj):
        if obj.icon:
            return f'<img src="{obj.icon.url}" width="50" height="50" style="border-radius: 5px;" />'
        return "Нет иконки"
    icon_preview.allow_tags = True
    icon_preview.short_description = "Превью иконки"

    def subcategories_count(self, obj):
        return obj.categories_set.filter(parent=obj).count()
    subcategories_count.short_description = "Количество подкатегорий"


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    readonly_fields = ['created_at']
    fields = ['name', 'parent', 'created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent__isnull=False)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = MainCategory.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'category', 'is_popular', 'created_at']
    list_filter = ['category', 'is_popular', 'created_at']
    search_fields = ['name', 'author', 'description']
    ordering = ['-created_at']


@admin.register(CourseChapter)
class CourseChapterAdmin(admin.ModelAdmin):
    list_display = ['course', 'title', 'is_activate', 'order', 'materials_count', 'total_duration']
    list_filter = ['course', 'is_activate', 'created_at']
    search_fields = ['title', 'course__name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

    def materials_count(self, obj):
        return obj.coursechaptermaterials_set.count()
    materials_count.short_description = "Количество материалов"

    def total_duration(self, obj):
        total_seconds = obj.get_total_duration()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        return f"{hours:02d}:{minutes:02d}"
    total_duration.short_description = "Общая длительность"


@admin.register(CourseChapterVideo)
class CourseChapterVideoAdmin(admin.ModelAdmin):
    list_display = ['chapter', 'title', 'is_activate', 'is_free']
    list_filter = ['chapter__course', 'is_activate', 'is_free']
    search_fields = ['title', 'chapter__title', 'chapter__course__name']
    ordering = ['chapter']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('chapter', 'title', 'description', 'is_activate', 'is_free')
        }),
        ('Видео файл', {
            'fields': ('video_file', 'video_time'),
            'classes': ('wide',),
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('chapter__course')
    
    def formfield_for_duration_field(self, db_field, request, **kwargs):
        if db_field.name == 'video_time':
            kwargs['widget'] = forms.TextInput(attrs={'placeholder': 'HH:MM:SS (например: 01:30:00)'})
        return super().formfield_for_duration_field(db_field, request, **kwargs)


@admin.register(CourseChapterMaterials)
class CourseChapterMaterialsAdmin(admin.ModelAdmin):
    list_display = ['chapter', 'title', 'material_type', 'is_activate', 'is_free']
    list_filter = ['chapter__course', 'material_type', 'is_activate', 'is_free']
    search_fields = ['title', 'chapter__title', 'chapter__course__name']
    ordering = ['chapter']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('chapter', 'title', 'description', 'material_type', 'is_activate', 'is_free')
        }),
        ('Файлы', {
            'fields': ('image_file', 'document_file'),
            'classes': ('wide',),
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    class Media:
        js = ('admin/js/course_materials_admin.js',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('chapter__course')
    
    def save_model(self, request, obj, form, change):
        """Override save to call clean method for validation"""
        obj.clean()
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Add custom widget attributes for JavaScript
        if 'material_type' in form.base_fields:
            form.base_fields['material_type'].widget.attrs.update({
                'onchange': 'toggleFileFields()'
            })
        
        return form


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    """Course review admin configuration"""
    list_display = ['course', 'first_name', 'last_name', 'rating', 'comment_preview', 'is_active', 'created_at']
    list_filter = ['course', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'comment', 'course__name']
    list_editable = ['is_active']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('course', 'user', 'first_name', 'last_name')
        }),
        ('Комментарий и рейтинг', {
            'fields': ('comment', 'rating')
        }),
        ('Состояние', {
            'fields': ('is_active',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def comment_preview(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = "Комментарий"


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1
    fk_name = 'quiz'
    verbose_name = 'Вопрос теста'
    verbose_name_plural = 'Вопросы теста'
    fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'explanation', 'is_active']
    readonly_fields = ['created_at']


@admin.register(CourseQuiz)
class CourseQuizAdmin(admin.ModelAdmin):
    """Course quiz admin configuration"""
    list_display = ['course', 'title', 'questions_count', 'passing_score', 'time_limit', 'is_active', 'created_at']
    list_filter = ['course', 'is_active', 'created_at']
    search_fields = ['title', 'course__name', 'description']
    list_editable = ['is_active']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [QuizQuestionInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('course', 'title', 'description', 'is_active')
        }),
        ('Настройки теста', {
            'fields': ('questions_count', 'passing_score', 'time_limit')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """Quiz question admin configuration"""
    list_display = ['quiz', 'question_preview', 'correct_answer', 'is_active', 'created_at']
    list_filter = ['quiz', 'is_active', 'created_at']
    search_fields = ['question_text', 'quiz__title', 'quiz__course__name']
    list_editable = ['is_active']
    ordering = ['quiz', 'created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('quiz', 'question_text', 'is_active')
        }),
        ('Варианты ответов', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
        }),
        ('Объяснение', {
            'fields': ('explanation',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def question_preview(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_preview.short_description = "Вопрос"


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    """Quiz attempt admin configuration"""
    list_display = ['user', 'quiz', 'score', 'percentage', 'is_passed', 'is_completed', 'started_at']
    list_filter = ['quiz', 'is_passed', 'is_completed', 'started_at']
    search_fields = ['user__email', 'quiz__title', 'quiz__course__name']
    ordering = ['-started_at']
    readonly_fields = ['started_at', 'completed_at', 'score', 'percentage', 'is_passed', 'time_taken']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'quiz', 'is_completed')
        }),
        ('Результаты', {
            'fields': ('score', 'percentage', 'is_passed', 'time_taken')
        }),
        ('Время', {
            'fields': ('started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Ответы', {
            'fields': ('answers',),
            'classes': ('collapse',)
        }),
    )


@admin.register(QuizCertificate)
class QuizCertificateAdmin(admin.ModelAdmin):
    """Quiz certificate admin configuration"""
    list_display = ['user', 'quiz', 'certificate_number', 'issued_at', 'is_active']
    list_filter = ['quiz', 'is_active', 'issued_at']
    search_fields = ['user__email', 'quiz__title', 'certificate_number']
    ordering = ['-issued_at']
    readonly_fields = ['certificate_number', 'issued_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'quiz', 'attempt', 'is_active')
        }),
        ('Сертификат', {
            'fields': ('certificate_number', 'issued_at'),
            'classes': ('collapse',)
        }),
    )

