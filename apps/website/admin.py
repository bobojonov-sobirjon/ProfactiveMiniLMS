from django.contrib import admin
from .models import FAQ, AboutSection, Blog, ReferralRequest, Document, DiscountForReferral, MainHeader, ReferralStep, ContactPage

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """FAQ admin configuration"""
    list_display = ['question', 'category', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['question', 'answer', 'category']
    list_editable = ['is_active', 'order']
    ordering = ['order', 'created_at']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('question', 'answer')
        }),
        ('Kategoriya va tartib', {
            'fields': ('category', 'order')
        }),
        ('Holat', {
            'fields': ('is_active',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('order', 'created_at')


@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    """About section admin configuration"""
    list_display = ['title_short', 'keywords', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description', 'keywords']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'keywords')
        }),
        ('Изображение', {
            'fields': ('image',)
        }),
        ('Кнопка', {
            'fields': ('button_text', 'button_url')
        }),
        ('Порядок и состояние', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def title_short(self, obj):
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
    title_short.short_description = "Заголовок"


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    """Blog admin configuration"""
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'image')
        }),
        ('Состояние', {
            'fields': ('is_active',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')

@admin.register(ReferralRequest)
class ReferralRequestAdmin(admin.ModelAdmin):
    """Referral request admin configuration"""
    list_display = ['first_name', 'last_name', 'email', 'promo_code', 'referral_user_info', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'referred_by']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number', 'promo_code', 'referred_by_name', 'referred_by_email']
    list_editable = ['is_active']
    ordering = ['-created_at']
    readonly_fields = ['promo_code', 'referral_link', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Реферальная информация', {
            'fields': ('promo_code', 'referral_link', 'is_active')
        }),
        ('Кто пригласил', {
            'fields': ('referred_by', 'referred_by_name', 'referred_by_email'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def referral_user_info(self, obj):
        if obj.referred_by_name:
            return f"Приглашен: {obj.referred_by_name}"
        return "Первый пользователь"
    referral_user_info.short_description = "Реферальная информация"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Document admin configuration"""
    list_display = ['title', 'file_type', 'file_size_display', 'download_count', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'file_type', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']
    ordering = ['order', 'created_at']
    readonly_fields = ['file_type', 'file_size', 'download_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'file')
        }),
        ('Информация о файле', {
            'fields': ('file_type', 'file_size', 'download_count'),
            'classes': ('collapse',)
        }),
        ('Порядок и состояние', {
            'fields': ('order', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = "Размер файла"


@admin.register(DiscountForReferral)
class DiscountForReferralAdmin(admin.ModelAdmin):
    """Discount for referral admin configuration"""
    list_display = ['id', 'percentage']
    list_display_links = ['id']
    search_fields = ['percentage']
    list_editable = ['percentage']
    
    fieldsets = (
        ('Процент скидки', {
            'fields': ('percentage',)
        }),
    )


@admin.register(ReferralStep)
class ReferralStepAdmin(admin.ModelAdmin):
    """Referral step admin configuration"""
    list_display = ['title_short', 'keywords', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description', 'keywords']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'keywords')
        }),
        ('Изображение', {
            'fields': ('image',)
        }),
        ('Порядок и состояние', {
            'fields': ('order', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_short(self, obj):
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
    title_short.short_description = "Заголовок"


@admin.register(MainHeader)
class MainHeaderAdmin(admin.ModelAdmin):
    """Main header admin configuration"""
    list_display = ['title_short', 'keywords', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'keywords']
    list_editable = ['is_active']
    ordering = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'keywords')
        }),
        ('Медиа файлы', {
            'fields': ('image', 'image_banner_video', 'video')
        }),
        ('Политика конфиденциальности', {
            'fields': ('privacy_policy_file',)
        }),
        ('Состояние', {
            'fields': ('is_active',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_short(self, obj):
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
    title_short.short_description = "Заголовок"


@admin.register(ContactPage)
class ContactPageAdmin(admin.ModelAdmin):
    """Contact page admin configuration"""
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title']
    list_editable = ['is_active']
    ordering = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'is_active')
        }),
        ('Карта', {
            'fields': ('map_iframe',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_short(self, obj):
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
    title_short.short_description = "Заголовок"