from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.core.exceptions import ValidationError

User = get_user_model()

@csrf_protect
def register_view(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        # Получаем данные из формы
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        patronymic = request.POST.get('patronymic', '').strip()
        
        # Валидация полей
        errors = []
        
        if not email:
            errors.append('Email обязателен')
        elif '@' not in email:
            errors.append('Введите корректный email')
        elif User.objects.filter(email=email).exists():
            errors.append('Пользователь с таким email уже существует')
        
        if not password:
            errors.append('Пароль обязателен')
        elif len(password) < 8:
            errors.append('Пароль должен содержать минимум 8 символов')
        
        if not confirm_password:
            errors.append('Подтвердите пароль')
        elif password != confirm_password:
            errors.append('Пароли не совпадают')
        
        if not first_name:
            errors.append('Имя обязательно')
        elif len(first_name) < 2:
            errors.append('Имя должно содержать минимум 2 символа')
        
        if not last_name:
            errors.append('Фамилия обязательна')
        elif len(last_name) < 2:
            errors.append('Фамилия должна содержать минимум 2 символа')
        
        # Если есть ошибки, показываем их
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'register.html', {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'patronymic': patronymic
            })
        
        # Создаем пользователя
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                patronymic=patronymic,
                is_active=True
            )
            
            # Автоматически входим в систему
            login(request, user)
            messages.success(request, f'Регистрация успешна! Добро пожаловать, {user.first_name}!')
            return redirect('profile')
            
        except Exception as e:
            messages.error(request, f'Ошибка при создании аккаунта: {str(e)}')
            return render(request, 'register.html', {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'patronymic': patronymic
            })
    
    return render(request, 'register.html')

@csrf_protect
def login_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        return redirect('profile')
    
    # Check for logout message in session
    if 'logout_message' in request.session:
        messages.success(request, request.session['logout_message'])
        del request.session['logout_message']
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Пожалуйста, заполните все поля')
            return render(request, 'login.html')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.first_name}!')
                return redirect('profile')
            else:
                messages.error(request, 'Ваш аккаунт деактивирован')
        else:
            messages.error(request, 'Неверный email или пароль')
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    # Use session to store message after logout
    request.session['logout_message'] = 'Вы успешно вышли из системы'
    return redirect('login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        
        # Update basic profile information
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.patronymic = request.POST.get('patronymic', user.patronymic).strip()
        
        # Password validation
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Check if user wants to change password
        if new_password or confirm_password:
            if not new_password:
                messages.error(request, 'Введите новый пароль')
                return render(request, 'personal-account.html', {'user': user})
            
            if not confirm_password:
                messages.error(request, 'Подтвердите новый пароль')
                return render(request, 'personal-account.html', {'user': user})
            
            if new_password != confirm_password:
                messages.error(request, 'Пароли не совпадают')
                return render(request, 'personal-account.html', {'user': user})
            
            if len(new_password) < 8:
                messages.error(request, 'Пароль должен содержать минимум 8 символов')
                return render(request, 'personal-account.html', {'user': user})
            
            # Set new password
            user.set_password(new_password)
            messages.success(request, 'Пароль успешно изменен')
        
        # Save user profile
        try:
            user.save()
            if not new_password:  # Only show profile update message if password wasn't changed
                messages.success(request, 'Профиль успешно обновлен')
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении профиля: {str(e)}')
            return render(request, 'personal-account.html', {'user': user})
    
        return render(request, 'personal-account.html', {'user': request.user})
    
    # GET request - just show the profile page
    return render(request, 'personal-account.html', {'user': request.user})

@csrf_protect
def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Email tekshirish
        if not email:
            messages.error(request, 'Введите email')
            return render(request, 'password-reset.html')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден')
            return render(request, 'password-reset.html')
        
        # Agar faqat email kiritilgan bo'lsa
        if not new_password and not confirm_password:
            messages.success(request, 'Email правильный. Введите новый пароль.')
            return render(request, 'password-reset.html', {'email': email, 'show_password_fields': True})
        
        # Agar password kiritilgan bo'lsa
        if new_password or confirm_password:
            if not new_password:
                messages.error(request, 'Введите новый пароль')
                return render(request, 'password-reset.html', {'email': email, 'show_password_fields': True})
            
            if not confirm_password:
                messages.error(request, 'Подтвердите пароль')
                return render(request, 'password-reset.html', {'email': email, 'show_password_fields': True})
            
            if new_password != confirm_password:
                messages.error(request, 'Пароли не совпадают')
                return render(request, 'password-reset.html', {'email': email, 'show_password_fields': True})
            
            if len(new_password) < 8:
                messages.error(request, 'Пароль должен содержать минимум 8 символов')
                return render(request, 'password-reset.html', {'email': email, 'show_password_fields': True})
            
            # Parolni yangilash
            user.set_password(new_password)
            user.save()
            
            messages.success(request, 'Пароль успешно изменен')
            return redirect('login')
    
    # GET request - show password reset page
    return render(request, 'password-reset.html')