from django.shortcuts import render
from django.http import HttpResponseNotFound, JsonResponse
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from .models import FAQ, AboutSection, Blog, ReferralRequest, Document, DiscountForReferral, MainHeader, ReferralStep, ContactPage
from apps.courses.models import Categories, Courses

def custom_404(request, exception=None):
    """Custom 404 error page view"""
    return render(request, '404.html', status=404)

def home(request):
    """Home page view"""
    # Get main categories (categories without parent)
    main_categories = Categories.objects.filter(parent__isnull=True).order_by('name')
    
    # Get popular courses
    popular_courses = Courses.objects.filter(is_popular=True).order_by('-created_at')
    
    # Get active main header
    main_header = MainHeader.get_active_header()
    
    context = {
        'main_categories': main_categories,
        'popular_courses': popular_courses,
        'referral_discount': DiscountForReferral.get_active_discount(),
        'main_header': main_header,
    }
    
    return render(request, 'index.html', context)

def about(request):
    """About page view"""
    # Get active about sections
    about_sections = AboutSection.objects.filter(is_active=True).order_by('order')
    
    context = {
        'about_sections': about_sections,
        'referral_discount': DiscountForReferral.get_active_discount(),
    }
    
    return render(request, 'about.html', context)

def services(request):
    """Services page view"""
    context = {
        'referral_discount': DiscountForReferral.get_active_discount(),
    }
    return render(request, 'services.html', context)

def course_catalogue(request):
    """Course catalogue page view"""
    from apps.courses.views import course_catalogue as courses_catalogue
    
    # Check if user came from referral link
    referral_promo_code = request.session.get('referral_promo_code')
    referral_user = request.session.get('referral_user')
    
    # Call the original course catalogue view
    response = courses_catalogue(request)
    
    # Add referral context if available
    if referral_promo_code and referral_user:
        if hasattr(response, 'context_data'):
            response.context_data['referral_promo_code'] = referral_promo_code
            response.context_data['referral_user'] = referral_user
        else:
            # If it's a direct render response, we need to modify the context
            pass
    
    return response

def materials(request):
    """Materials page view"""
    context = {
        'referral_discount': DiscountForReferral.get_active_discount(),
    }
    return render(request, 'materials.html', context)

def popular(request):
    """Popular courses page view"""
    context = {
        'referral_discount': DiscountForReferral.get_active_discount(),
    }
    return render(request, 'popular.html', context)

def referal(request):
    """Referral program page view"""
    # Get active referral steps
    referral_steps = ReferralStep.objects.filter(is_active=True).order_by('order')
    
    context = {
        'referral_steps': referral_steps,
        'referral_discount': DiscountForReferral.get_active_discount(),
    }
    return render(request, 'referal.html', context)

def contacts(request):
    """Contacts page view"""
    # Get active contact page
    contact_page = ContactPage.get_active_contact_page()
    
    context = {
        'contact_page': contact_page,
        'referral_discount': DiscountForReferral.get_active_discount(),
    }
    return render(request, 'contacts.html', context)

def login(request):
    """Login page view - redirect to accounts login"""
    from django.shortcuts import redirect
    return redirect('/accounts/login/')

def documentation(request):
    """Documentation page view"""
    context = {
        'referral_discount': DiscountForReferral.get_active_discount(),
    }
    return render(request, 'documentation.html', context)

def get_faqs(request):
    """FAQ page view"""
    faqs = FAQ.objects.filter(is_active=True).order_by('order', 'created_at')
    context = {
        'faqs': faqs,
        'referral_discount': DiscountForReferral.get_active_discount(),
    }
    return render(request, 'faq.html', context)

def blog(request):
    """Blog page view with Alpine.js show more functionality"""
    blogs = Blog.objects.filter(is_active=True).order_by('-created_at')
    
    context = {
        'blogs': blogs,
    }
    
    return render(request, 'blog.html', context)


def referal_request(request):
    """Handle referral request form submission"""
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            
            if not all([first_name, last_name, email, phone_number]):
                return JsonResponse({
                    'success': False,
                    'message': 'Все поля обязательны для заполнения'
                })
            
            # Allow multiple referrals from the same email
            # No need to check for existing email
            
            # Create referral request
            referral = ReferralRequest.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number
            )
            
            # Send email with referral link and promo code
            subject = 'Ваша реферальная ссылка и промокод - Profactive'
            
            message = f'''
Здравствуйте, {first_name} {last_name}!

Добро пожаловать в реферальную программу Profactive!

Ваши данные:
- Промокод: {referral.promo_code}
- Реферальная ссылка: {referral.referral_link}

Как использовать:
1. Поделитесь ссылкой с друзьями
2. Когда друг перейдет по ссылке и купит курс, вы получите 6% от суммы
3. Промокод можно использовать для получения скидки при покупке курсов

С уважением,
Команда PROFACTIVE
            '''
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending referral email: {e}")
            
            return JsonResponse({
                'success': True,
                'message': 'Новая реферальная ссылка отправлена на ваш email. Вы можете создавать несколько реферальных ссылок.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Ошибка при создании заявки: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'})


def referral_redirect(request, promo_code):
    """Redirect users from referral links to courses page"""
    try:
        # Check if promo code exists
        referral = ReferralRequest.objects.get(promo_code=promo_code, is_active=True)
        
        # Store promo code and referral info in session for later use
        request.session['referral_promo_code'] = promo_code
        request.session['referral_user'] = f"{referral.first_name} {referral.last_name}"
        request.session['referral_user_email'] = referral.email
        
        # Redirect to courses page
        from django.shortcuts import redirect
        return redirect('course-catalogue')
        
    except ReferralRequest.DoesNotExist:
        # If promo code doesn't exist, still redirect to courses but without referral data
        from django.shortcuts import redirect
        return redirect('course-catalogue')


def documents_page(request):
    """Documents page view"""
    documents = Document.objects.filter(is_active=True).order_by('order', 'created_at')
    
    context = {
        'documents': documents,
    }
    
    return render(request, 'documents.html', context)


def download_document(request, document_id):
    """Download document view"""
    try:
        document = Document.objects.get(id=document_id, is_active=True)
        
        # Увеличиваем счетчик скачиваний
        document.download_count += 1
        document.save(update_fields=['download_count'])
        
        # Возвращаем файл для скачивания
        from django.http import FileResponse
        response = FileResponse(document.file, as_attachment=True, filename=document.title)
        return response
        
    except Document.DoesNotExist:
        return HttpResponseNotFound("Документ не найден")


def download_privacy_policy(request):
    """Download privacy policy file view"""
    try:
        main_header = MainHeader.get_active_header()
        
        if not main_header or not main_header.privacy_policy_file:
            return HttpResponseNotFound("Файл политики конфиденциальности не найден")
        
        # Возвращаем файл для скачивания
        from django.http import FileResponse
        response = FileResponse(
            main_header.privacy_policy_file, 
            as_attachment=True, 
            filename="Политика_конфиденциальности.pdf"
        )
        return response
        
    except Exception as e:
        return HttpResponseNotFound("Ошибка при загрузке файла")
