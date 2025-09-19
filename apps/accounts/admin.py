from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'last_name', 'first_name', 'patronymic')
        labels = {
            'email': _('Email адрес'),
            'last_name': _('Фамилия'),
            'first_name': _('Имя'),
            'patronymic': _('Отчество'),
        }
        help_texts = {
            'email': _('Введите действующий email адрес'),
            'last_name': _('Введите фамилию пользователя'),
            'first_name': _('Введите имя пользователя'),
            'patronymic': _('Введите отчество пользователя (необязательно)'),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Store the raw password before hashing
        user._raw_password = self.cleaned_data.get('password1')
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
        labels = {
            'email': _('Email адрес'),
            'last_name': _('Фамилия'),
            'first_name': _('Имя'),
            'patronymic': _('Отчество'),
            'is_deleted': _('Удален'),
            'is_active': _('Активен'),
            'is_staff': _('Персонал'),
            'is_superuser': _('Суперпользователь'),
            'date_joined': _('Дата регистрации'),
            'last_login': _('Последний вход'),
        }
        help_texts = {
            'email': _('Введите действующий email адрес'),
            'last_name': _('Введите фамилию пользователя'),
            'first_name': _('Введите имя пользователя'),
            'patronymic': _('Введите отчество пользователя (необязательно)'),
            'is_deleted': _('Отметьте, если пользователь удален'),
            'is_active': _('Отметьте, если пользователь активен'),
            'is_staff': _('Отметьте, если пользователь является сотрудником'),
            'is_superuser': _('Отметьте, если пользователь имеет права суперпользователя'),
        }


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Заголовки для списка пользователей
    list_display = ('email', 'last_name', 'first_name', 'patronymic', 'is_deleted', 'is_active', 'is_staff', 'date_joined')
    list_display_links = ('email', 'last_name', 'first_name')
    list_filter = ('is_deleted', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'last_name', 'first_name', 'patronymic')
    ordering = ('email',)
    
    # Заголовки для полей в списке
    list_display_labels = {
        'email': _('Email'),
        'last_name': _('Фамилия'),
        'first_name': _('Имя'),
        'patronymic': _('Отчество'),
        'is_deleted': _('Удален'),
        'is_active': _('Активен'),
        'is_staff': _('Персонал'),
        'date_joined': _('Дата регистрации'),
    }
    
    # Override UserAdmin attributes that don't exist in our model
    filter_horizontal = ()
    raw_id_fields = ()
    
    fieldsets = (
        (None, {
            'fields': ('email', 'password'),
            'description': _('Основная информация для входа в систему')
        }),
        (_('Персональная информация'), {
            'fields': ('last_name', 'first_name', 'patronymic'),
            'description': _('Личные данные пользователя')
        }),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_deleted'),
            'description': _('Настройки доступа и статуса пользователя')
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'date_joined'),
            'description': _('Информация о времени входа и регистрации')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'last_name', 'first_name', 'patronymic', 'password1', 'password2'),
            'description': _('Создание нового пользователя')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('date_joined',)
        return self.readonly_fields
    
    def get_queryset(self, request):
        """Фильтрация пользователей для отображения"""
        qs = super().get_queryset(request)
        return qs
    
    def get_list_display(self, request):
        """Динамическое отображение полей в зависимости от прав"""
        list_display = list(super().get_list_display(request))
        if not request.user.is_superuser:
            # Обычные администраторы не видят поле is_superuser
            if 'is_superuser' in list_display:
                list_display.remove('is_superuser')
        return list_display


# Настройка заголовков админ-панели
admin.site.site_header = _('Администрирование Profactive')
admin.site.site_title = _('Profactive Админ')
admin.site.index_title = _('Панель управления')


# Отключение группы пользователей
admin.site.unregister(Group)

