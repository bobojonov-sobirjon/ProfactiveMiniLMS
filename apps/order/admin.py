from django.contrib import admin
from .models import (
    CourseOrder, 
    CourseChapterForOrderedUser, 
    CourseVideoForOrderedUser, 
    CourseMaterialForOrderedUser,
    UserVideoProgress
)


@admin.register(CourseOrder)
class CourseOrderAdmin(admin.ModelAdmin):
    list_display = ['sender', 'course', 'order_date', 'is_active', 'is_completed']
    list_filter = ['is_active', 'is_completed', 'order_date', 'course__category']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'course__name']
    readonly_fields = ['order_date']
    list_editable = ['is_active', 'is_completed']
    ordering = ['-order_date']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('sender', 'course', 'order_date')
        }),
        ('Статус заказа', {
            'fields': ('is_active', 'is_completed')
        }),
        ('Дополнительно', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


class CourseVideoForOrderedUserInline(admin.TabularInline):
    model = CourseVideoForOrderedUser
    extra = 0
    fields = ['title', 'video_file', 'video_time', 'is_activate', 'is_accessible', 'video_order']
    readonly_fields = ['access_granted_date']


class CourseMaterialForOrderedUserInline(admin.TabularInline):
    model = CourseMaterialForOrderedUser
    extra = 0
    fields = ['title', 'material_type', 'is_activate', 'is_accessible', 'material_order']
    readonly_fields = ['access_granted_date']


@admin.register(CourseChapterForOrderedUser)
class CourseChapterForOrderedUserAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'chapter_order', 'is_activate', 'is_accessible', 'access_granted_date']
    list_filter = ['is_activate', 'is_accessible', 'access_granted_date', 'order__course']
    search_fields = ['title', 'order__user__email', 'order__course__name']
    readonly_fields = ['access_granted_date']
    list_editable = ['is_activate', 'is_accessible', 'chapter_order']
    ordering = ['order', 'chapter_order']
    
    inlines = [CourseVideoForOrderedUserInline, CourseMaterialForOrderedUserInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('order', 'title', 'description', 'chapter_order')
        }),
        ('Статус', {
            'fields': ('is_activate', 'is_accessible', 'access_granted_date')
        }),
    )


@admin.register(CourseVideoForOrderedUser)
class CourseVideoForOrderedUserAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'chapter', 'video_time', 'video_order', 'is_activate', 'is_accessible', 'access_granted_date']
    list_filter = ['is_activate', 'is_accessible', 'is_free', 'access_granted_date', 'order__course']
    search_fields = ['title', 'order__user__email', 'order__course__name', 'chapter__title']
    readonly_fields = ['access_granted_date']
    list_editable = ['is_activate', 'is_accessible', 'video_order']
    ordering = ['order', 'video_order']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('order', 'chapter', 'title', 'description', 'video_order')
        }),
        ('Видео файл', {
            'fields': ('video_file', 'video_time')
        }),
        ('Статус', {
            'fields': ('is_activate', 'is_free', 'is_accessible', 'access_granted_date')
        }),
    )


@admin.register(CourseMaterialForOrderedUser)
class CourseMaterialForOrderedUserAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'chapter', 'material_type', 'material_order', 'is_activate', 'is_accessible', 'access_granted_date']
    list_filter = ['material_type', 'is_activate', 'is_accessible', 'is_free', 'access_granted_date', 'order__course']
    search_fields = ['title', 'order__user__email', 'order__course__name', 'chapter__title']
    readonly_fields = ['access_granted_date']
    list_editable = ['is_activate', 'is_accessible', 'material_order']
    ordering = ['order', 'material_order']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('order', 'chapter', 'title', 'description', 'material_type', 'material_order')
        }),
        ('Файлы', {
            'fields': ('image_file', 'document_file')
        }),
        ('Статус', {
            'fields': ('is_activate', 'is_free', 'is_accessible', 'access_granted_date')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'chapter', 'order__user', 'order__course')


@admin.register(UserVideoProgress)
class UserVideoProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'is_watched', 'watched_at', 'watch_duration']
    list_filter = ['is_watched', 'watched_at', 'video__order__course']
    search_fields = ['user__email', 'video__title', 'video__order__course__name']
    readonly_fields = ['watched_at']
    list_editable = ['is_watched']
    ordering = ['-watched_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'video', 'is_watched', 'watched_at')
        }),
        ('Детали просмотра', {
            'fields': ('watch_duration',)
        }),
    )
