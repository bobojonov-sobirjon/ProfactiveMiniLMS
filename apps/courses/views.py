from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import json
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from .models import Courses, CourseChapter, CourseChapterVideo, CourseChapterMaterials, Categories, CourseReview, CourseQuiz, QuizQuestion, QuizAttempt, QuizCertificate
from apps.website.models import DiscountForReferral
from apps.order.models import CourseOrder, CourseChapterForOrderedUser, CourseVideoForOrderedUser, CourseMaterialForOrderedUser, UserVideoProgress, UserChapterProgress


def course_detail(request, course_id):
    """Course detail page view"""
    course = get_object_or_404(Courses, id=course_id)
    
    # Get course chapters with their materials
    chapters = CourseChapter.objects.filter(course=course).order_by('order')
    
    # Get course videos
    videos = CourseChapterVideo.objects.filter(chapter__course=course, is_activate=True).order_by('chapter__order', 'order')
    
    # Get course materials (documents and images)
    materials = CourseChapterMaterials.objects.filter(chapter__course=course, is_activate=True).order_by('chapter__order', 'order')
    
    # Get related courses (same category)
    related_courses = Courses.objects.filter(
        category=course.category
    ).exclude(id=course.id).order_by('-created_at')[:4]
    
    # Calculate course statistics
    total_lessons = videos.count()
    total_duration_seconds = sum(video.video_time.total_seconds() for video in videos)
    total_duration_hours = int(total_duration_seconds // 3600)
    total_duration_minutes = int((total_duration_seconds % 3600) // 60)
    
    # Organize chapters with their content
    chapters_with_content = []
    for chapter in chapters:
        chapter_videos = videos.filter(chapter=chapter)
        chapter_materials = materials.filter(chapter=chapter)
        
        # Calculate total video duration for this chapter
        chapter_duration_seconds = sum(video.video_time.total_seconds() for video in chapter_videos)
        chapter_duration_hours = int(chapter_duration_seconds // 3600)
        chapter_duration_minutes = int((chapter_duration_seconds % 3600) // 60)
        
        chapters_with_content.append({
            'chapter': chapter,
            'videos': chapter_videos,
            'materials': chapter_materials,
            'total_items': chapter_videos.count() + chapter_materials.count(),
            'total_duration_seconds': chapter_duration_seconds,
            'total_duration_hours': chapter_duration_hours,
            'total_duration_minutes': chapter_duration_minutes
        })
    
    # Check if user is enrolled (for authenticated users)
    is_enrolled = False
    if request.user.is_authenticated:
        from apps.accounts.models import CourseEnrollment
        is_enrolled = CourseEnrollment.objects.filter(
            user=request.user,
            course=course
        ).exists()
    
    # Get active reviews for this course
    reviews = CourseReview.objects.filter(course=course, is_active=True).order_by('-created_at')[:5]
    
    context = {
        'course': course,
        'chapters': chapters,
        'videos': videos,
        'materials': materials,
        'chapters_with_content': chapters_with_content,
        'related_courses': related_courses,
        'total_lessons': total_lessons,
        'total_duration_hours': total_duration_hours,
        'total_duration_minutes': total_duration_minutes,
        'is_enrolled': is_enrolled,
        'reviews': reviews,
        'referral_discount': DiscountForReferral.get_active_discount(),
    }
    
    return render(request, 'we-course.html', context)


def course_catalogue(request):
    """Course catalogue page view"""
    # Get filter parameters
    main_category_id = request.GET.get('main_category')
    sub_category_id = request.GET.get('sub_category')
    search_query = request.GET.get('search')
    is_popular_filter = request.GET.get('is_popular') == 'true'
    
    # Start with all courses (remove is_activate filter as it doesn't exist in model)
    courses = Courses.objects.all().order_by('-created_at')
    
    # Filter by category - prioritize sub category over main category
    if sub_category_id:
        courses = courses.filter(category_id=sub_category_id)
    elif main_category_id:
        # If main category is selected, get all courses from that category and its subcategories
        try:
            main_category = Categories.objects.get(id=main_category_id)
            subcategory_ids = list(main_category.categories_set.values_list('id', flat=True))
            subcategory_ids.append(main_category_id)
            courses = courses.filter(category_id__in=subcategory_ids)
        except Categories.DoesNotExist:
            courses = courses.none()
    
    # Filter by search query if specified
    if search_query:
        courses = courses.filter(
            name__icontains=search_query
        ) | courses.filter(
            description__icontains=search_query
        ) | courses.filter(
            author__icontains=search_query
        )
    
    # Filter by popular courses if specified
    if is_popular_filter:
        courses = courses.filter(is_popular=True)
    
    # Get all courses for "show more" functionality
    all_courses = courses
    
    # Get main categories (categories without parent) with their subcategories
    main_categories = Categories.objects.filter(parent__isnull=True).prefetch_related('categories_set').order_by('name')
    
    # For AJAX requests, return only the courses container
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'courses-container.html', {
            'courses': all_courses,
            'selected_sub_category': sub_category_id,
            'is_popular_filter': is_popular_filter,
            'referral_discount': DiscountForReferral.get_active_discount(),
        })
    
    context = {
        'courses': all_courses,
        'main_categories': main_categories,
        'selected_main_category': main_category_id,
        'selected_sub_category': sub_category_id,
        'search_query': search_query,
        'is_popular_filter': is_popular_filter,
        'referral_discount': DiscountForReferral.get_active_discount(),
    }
    
    return render(request, 'course-catalogue.html', context)


def create_course_review(request, course_id):
    """Create a course review/comment"""
    if request.method == 'POST':
        try:
            course = get_object_or_404(Courses, id=course_id)
            
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            comment = request.POST.get('comment')
            rating = request.POST.get('rating')
            
            if not all([first_name, last_name, comment, rating]):
                return JsonResponse({
                    'success': False,
                    'message': 'Все поля обязательны для заполнения'
                })
            
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    raise ValueError("Invalid rating")
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': 'Неверный рейтинг'
                })
            
            # Check if user already reviewed this course
            if request.user.is_authenticated:
                existing_review = CourseReview.objects.filter(
                    course=course, 
                    user=request.user
                ).first()
                if existing_review:
                    return JsonResponse({
                        'success': False,
                        'message': 'Вы уже оставили отзыв для этого курса'
                    })
            
            # Create the review
            review = CourseReview.objects.create(
                course=course,
                user=request.user if request.user.is_authenticated else None,
                first_name=first_name,
                last_name=last_name,
                comment=comment,
                rating=rating,
                is_active=False  # Admin needs to approve
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Ваш отзыв отправлен на модерацию'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Ошибка при создании отзыва: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'})


def reviews_page(request):
    """Reviews page showing all active reviews"""
    reviews = CourseReview.objects.filter(is_active=True).select_related('course', 'user')
    print(reviews)
    
    # Pagination
    paginator = Paginator(reviews, 10)  # 10 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reviews': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'reviews.html', context)


def popular_courses(request):
    """Popular courses page view"""
    popular_courses = Courses.objects.filter(
        is_popular=True, 
        is_activate=True
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(popular_courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'popular.html', context)


@login_required
def enroll_course(request, course_id):
    """Enroll user in a course"""
    if request.method == 'POST':
        course = get_object_or_404(Courses, id=course_id)
        
        # Check if user is already enrolled
        from apps.accounts.models import CourseEnrollment
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course
        )
        
        if created:
            messages.success(request, f'Вы успешно записались на курс "{course.name}"')
        else:
            messages.info(request, f'Вы уже записаны на курс "{course.name}"')
        
        return redirect('courses:course_detail', course_id=course_id)
    
    return redirect('courses:course_detail', course_id=course_id)


@login_required
def get_access(request, course_id):
    """Get access to a course page"""
    course = get_object_or_404(Courses, id=course_id)
    
    # Check if user is already enrolled
    from apps.accounts.models import CourseEnrollment
    is_enrolled = CourseEnrollment.objects.filter(
        user=request.user,
        course=course
    ).exists()
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
    }
    
    return render(request, 'get-access.html', context)


@login_required
def my_courses(request):
    """User's enrolled courses page"""
    from apps.accounts.models import CourseEnrollment
    
    enrollments = CourseEnrollment.objects.filter(
        user=request.user
    ).select_related('course').order_by('-enrolled_at')
    
    context = {
        'enrollments': enrollments,
    }
    
    return render(request, 'my-courses.html', context)


@require_http_methods(["GET"])
def get_subcategories(request):
    """AJAX endpoint to get subcategories for a main category"""
    main_category_id = request.GET.get('main_category_id')
    
    if not main_category_id:
        return JsonResponse({'subcategories': []})
    
    try:
        subcategories = Categories.objects.filter(
            parent_id=main_category_id
        ).values('id', 'name').order_by('name')
        
        return JsonResponse({
            'subcategories': list(subcategories)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def create_course_order(request, course_id):
    """Create a course order and copy all course content"""
    if request.method == 'POST':
        try:
            course = get_object_or_404(Courses, id=course_id)
            
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            promo_code = request.POST.get('promo_code', '')
            
            if not all([first_name, last_name, email, phone_number]):
                return JsonResponse({
                    'success': False,
                    'message': 'Все поля обязательны для заполнения'
                })
            
            # Check if order already exists for this email
            existing_order = CourseOrder.objects.filter(sender=email, course=course).first()
            if existing_order:
                return JsonResponse({
                    'success': False,
                    'message': 'Вы уже заказали этот курс'
                })
            
            # Validate promo code if provided
            discount_percentage = 0
            referral_sender = None
            if promo_code:
                from apps.website.models import ReferralRequest
                try:
                    referral = ReferralRequest.objects.get(promo_code=promo_code, is_active=True)
                    # Get discount from database or use default
                    from apps.website.models import DiscountForReferral
                    discount_obj = DiscountForReferral.get_active_discount()
                    discount_percentage = float(discount_obj.percentage) if discount_obj else 6
                    referral_sender = referral
                except ReferralRequest.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'Неверный промокод'
                    })
            
            # Create the order
            order = CourseOrder.objects.create(
                user=request.user if request.user.is_authenticated else None,
                course=course,
                sender=email,
                is_active=False,  # Admin needs to activate
                is_completed=False,
                notes=f"Имя: {first_name} {last_name}, Телефон: {phone_number}, Промокод: {promo_code}, Скидка: {discount_percentage}%"
            )
            
            # Create referral request for the new user if they used a promo code
            if referral_sender and promo_code:
                from apps.website.models import ReferralRequest
                new_referral = ReferralRequest.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_number,
                    referred_by=referral_sender,
                    referred_by_name=f"{referral_sender.first_name} {referral_sender.last_name}",
                    referred_by_email=referral_sender.email
                )
            
            # If user is authenticated, create referral request for them too
            if request.user.is_authenticated:
                from apps.website.models import ReferralRequest
                # Check if user already has a referral request
                user_referral, created = ReferralRequest.objects.get_or_create(
                    email=request.user.email,
                    defaults={
                        'first_name': request.user.first_name or first_name,
                        'last_name': request.user.last_name or last_name,
                        'phone_number': phone_number,
                        'referred_by': referral_sender if referral_sender else None,
                        'referred_by_name': f"{referral_sender.first_name} {referral_sender.last_name}" if referral_sender else None,
                        'referred_by_email': referral_sender.email if referral_sender else None
                    }
                )
                if not created and referral_sender:
                    # Update existing referral with new referrer info
                    user_referral.referred_by = referral_sender
                    user_referral.referred_by_name = f"{referral_sender.first_name} {referral_sender.last_name}"
                    user_referral.referred_by_email = referral_sender.email
                    user_referral.save()
            
            # Copy all chapters
            chapters = CourseChapter.objects.filter(course=course, is_activate=True)
            for chapter in chapters:
                ordered_chapter, created = CourseChapterForOrderedUser.objects.get_or_create(
                    order=order,
                    title=chapter.title,
                    chapter_order=chapter.order,
                    defaults={
                        'description': chapter.description,
                        'is_activate': chapter.is_activate,
                        'is_accessible': False  # No access until admin activates
                    }
                )
                
                # Copy videos for this chapter
                videos = CourseChapterVideo.objects.filter(chapter=chapter, is_activate=True)
                for video in videos:
                    CourseVideoForOrderedUser.objects.get_or_create(
                        order=order,
                        title=video.title,
                        video_order=video.order,
                        defaults={
                            'chapter': ordered_chapter,
                            'description': video.description,
                            'video_file': video.video_file,
                            'video_time': video.video_time,
                            'is_activate': video.is_activate,
                            'is_free': video.is_free,
                            'is_accessible': False  # No access until admin activates
                        }
                    )
                
                # Copy materials for this chapter
                materials = CourseChapterMaterials.objects.filter(chapter=chapter, is_activate=True)
                for material in materials:
                    CourseMaterialForOrderedUser.objects.get_or_create(
                        order=order,
                        title=material.title,
                        material_order=material.order,
                        defaults={
                            'chapter': ordered_chapter,
                            'description': material.description,
                            'material_type': material.material_type,
                            'image_file': material.image_file,
                            'document_file': material.document_file,
                            'is_activate': material.is_activate,
                            'is_free': material.is_free,
                            'is_accessible': False  # No access until admin activates
                        }
                    )
            
            # Send email notification
            try:
                subject = f'Новая заявка на курс: {course.name}'
                message = f'''
Здравствуйте!

Поступила новая заявка на покупку курса:

Курс: {course.name}
Имя: {first_name} {last_name}
Email: {email}
Телефон: {phone_number}
Промокод: {promo_code if promo_code else 'Не указан'}
Скидка: {discount_percentage}%
Дата заявки: {order.order_date.strftime("%d.%m.%Y %H:%M")}

Пожалуйста, рассмотрите заявку и активируйте доступ к курсу.

С уважением,
Система PROFACTIVE
                '''
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending email: {e}")
                # Don't fail the order creation if email fails
            
            return JsonResponse({
                'success': True,
                'message': 'Ваша заявка отправлена администратору на рассмотрение'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Ошибка при создании заказа: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'})


@login_required
def my_courses(request):
    """Display user's ordered courses"""
    orders = CourseOrder.objects.filter(user=request.user).select_related('course')
    
    context = {
        'orders': orders
    }
    return render(request, 'my-courses.html', context)


@login_required
def ordered_course_detail(request, order_id):
    """Display detailed view of ordered course"""
    order = get_object_or_404(CourseOrder, id=order_id, user=request.user)
    
    # Get chapters with their content
    chapters = CourseChapterForOrderedUser.objects.filter(
        order=order
    ).prefetch_related(
        'coursevideoforordereduser_set',
        'coursematerialforordereduser_set'
    ).order_by('chapter_order')
    
    # Force update access if order is active but content is not accessible
    if order.is_active:
        updated_chapters = CourseChapterForOrderedUser.objects.filter(order=order, is_accessible=False).update(is_accessible=True)
        updated_videos = CourseVideoForOrderedUser.objects.filter(order=order, is_accessible=False).update(is_accessible=True)
        updated_materials = CourseMaterialForOrderedUser.objects.filter(order=order, is_accessible=False).update(is_accessible=True)
        
        # Refresh chapters after update
        if updated_chapters > 0 or updated_videos > 0 or updated_materials > 0:
            chapters = CourseChapterForOrderedUser.objects.filter(
                order=order
            ).prefetch_related(
                'coursevideoforordereduser_set',
                'coursematerialforordereduser_set'
            ).order_by('chapter_order')
    
    # Add progressive access logic and video watched status
    chapters_list = list(chapters)
    
    # Get all user video progress for this user
    user_video_progress = UserVideoProgress.objects.filter(
        user=request.user,
        is_watched=True
    ).values_list('video_id', flat=True)
    
    for i, chapter in enumerate(chapters_list):
        # Check chapter accessibility
        if i == 0:
            # First chapter is always accessible
            chapter.is_accessible = True
        else:
            # Subsequent chapters are accessible only if previous chapter is completed
            previous_chapter = chapters_list[i - 1]
            previous_progress = UserChapterProgress.objects.filter(
                user=request.user,
                chapter=previous_chapter,
                is_completed=True
            ).exists()
            chapter.is_accessible = previous_progress
        
        # Get videos with progressive access
        videos = chapter.coursevideoforordereduser_set.all().order_by('video_order')
        videos_list = list(videos)
        
        for j, video in enumerate(videos_list):
            if j == 0:
                # First video in chapter is accessible if chapter is accessible
                video.is_accessible = chapter.is_accessible
            else:
                # Subsequent videos are accessible only if previous video is watched AND chapter is accessible
                previous_video = videos_list[j-1]
                previous_watched = previous_video.id in user_video_progress
                video.is_accessible = previous_watched and chapter.is_accessible
            
            # Check if video is watched
            video.is_watched = video.id in user_video_progress
        
        # Check if chapter is completed
        total_videos = videos.count()
        watched_videos = sum(1 for video in videos_list if video.id in user_video_progress)
        chapter.is_completed = total_videos > 0 and watched_videos == total_videos
        
        # Materials are accessible if chapter is accessible and at least one video is watched
        for material in chapter.coursematerialforordereduser_set.all():
            # Material is accessible if chapter is accessible and at least one video is watched
            has_watched_video = any(video.id in user_video_progress for video in videos_list)
            material.is_accessible = chapter.is_accessible and has_watched_video
    
    # Calculate total lessons and duration
    total_lessons = sum(
        chapter.coursevideoforordereduser_set.count() + 
        chapter.coursematerialforordereduser_set.count()
        for chapter in chapters
    )
    
    total_duration_seconds = sum(
        video.video_time.total_seconds()
        for chapter in chapters
        for video in chapter.coursevideoforordereduser_set.all()
    )
    
    total_duration_hours = int(total_duration_seconds // 3600)
    total_duration_minutes = int((total_duration_seconds % 3600) // 60)
    
    # Check if all chapters are completed
    all_chapters_completed = all(chapter.is_completed for chapter in chapters_list)
    
    # Calculate progress data for the progress card
    # Get all videos for this order
    all_videos = CourseVideoForOrderedUser.objects.filter(order=order, is_accessible=True)
    total_videos = all_videos.count()
    
    # Count watched videos from progress tracking
    watched_videos = UserVideoProgress.objects.filter(
        user=request.user, 
        video__in=all_videos, 
        is_watched=True
    ).count()
    
    # Check if course has a quiz
    has_quiz = False
    quiz_passed = False
    try:
        quiz = CourseQuiz.objects.get(course=order.course, is_active=True)
        has_quiz = True
        quiz_attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-started_at').first()
        if quiz_attempt:
            quiz_passed = quiz_attempt.is_passed
    except CourseQuiz.DoesNotExist:
        pass
    
    # Calculate progress percentage based on video completion and quiz status
    if total_videos > 0:
        video_progress = (watched_videos / total_videos * 100)
        
        if has_quiz:
            # If course has quiz, max progress is 90% until quiz is passed
            if quiz_passed:
                progress_percentage = 100  # 100% only after passing quiz
            else:
                progress_percentage = min(90, video_progress)  # Max 90% for video completion
        else:
            # If no quiz, progress is based on video completion only
            progress_percentage = video_progress
    else:
        progress_percentage = 0
    
    # Ensure progress is never negative and never exceeds 100
    progress_percentage = max(0, min(100, progress_percentage))
    
    # Get quiz information
    quiz_attempt = None
    quiz_certificate = None
    
    try:
        quiz = CourseQuiz.objects.get(course=order.course, is_active=True)
        # Get the latest attempt (most recent one)
        quiz_attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-started_at').first()
        if quiz_attempt and quiz_attempt.is_passed:
            quiz_certificate = QuizCertificate.objects.filter(user=request.user, quiz=quiz).first()
    except CourseQuiz.DoesNotExist:
        pass
    
    context = {
        'order': order,
        'course': order.course,
        'chapters': chapters,
        'total_lessons': total_lessons,
        'total_duration_hours': total_duration_hours,
        'total_duration_minutes': total_duration_minutes,
        'is_enrolled': order.is_active,  # Access based on order status
        'quiz_attempt': quiz_attempt,
        'quiz_certificate': quiz_certificate,
        'all_chapters_completed': all_chapters_completed,
        # Progress data for the progress card
        'total_videos': total_videos,
        'watched_videos': watched_videos,
        'progress_percentage': round(progress_percentage, 1),
    }
    return render(request, 'ordered-course-detail.html', context)


@login_required
def course_results(request):
    """Display user's course progress and results"""
    # Get all active orders for the user
    orders = CourseOrder.objects.filter(user=request.user, is_active=True).select_related('course')
    
    course_progress = []
    
    for order in orders:
        # Get all videos for this order
        videos = CourseVideoForOrderedUser.objects.filter(order=order, is_accessible=True)
        total_videos = videos.count()
        
        # Count watched videos from progress tracking
        watched_videos = UserVideoProgress.objects.filter(
            user=request.user, 
            video__in=videos, 
            is_watched=True
        ).count()
        
        # Get quiz information first
        quiz_attempt = None
        quiz_passed = False
        has_quiz = False
        try:
            quiz = CourseQuiz.objects.get(course=order.course, is_active=True)
            has_quiz = True
            quiz_attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-started_at').first()
            if quiz_attempt:
                quiz_passed = quiz_attempt.is_passed
        except CourseQuiz.DoesNotExist:
            pass
        
        # Calculate progress percentage based on video completion and quiz status
        if total_videos > 0:
            video_progress = (watched_videos / total_videos * 100)
            
            if has_quiz:
                # If course has quiz, max progress is 90% until quiz is passed
                if quiz_passed:
                    progress_percentage = 100  # 100% only after passing quiz
                else:
                    progress_percentage = min(90, video_progress)  # Max 90% for video completion
            else:
                # If no quiz, progress is based on video completion only
                progress_percentage = video_progress
        else:
            progress_percentage = 0
        
        # Ensure progress is never negative and never exceeds 100
        progress_percentage = max(0, min(100, progress_percentage))
        
        course_data = {
            'order': order,
            'course': order.course,
            'total_videos': total_videos,
            'watched_videos': watched_videos,
            'progress_percentage': round(progress_percentage, 1),
            'is_completed': progress_percentage >= 100,
            'quiz_attempt': quiz_attempt,
            'quiz_passed': quiz_passed
        }
        
        course_progress.append(course_data)
    
    context = {
        'course_progress': course_progress
    }
    return render(request, 'course-results.html', context)


@login_required
@csrf_exempt
def mark_video_watched(request):
    """Mark a video as watched and update progress"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            video_id = data.get('video_id')
            
            if not video_id:
                return JsonResponse({'success': False, 'message': 'Video ID is required'})
            
            # Get the video
            video = get_object_or_404(CourseVideoForOrderedUser, id=video_id)
            
            # Check if user has access to this video
            if video.order.user != request.user:
                return JsonResponse({'success': False, 'message': 'Access denied'})
            
            # Mark video as watched
            progress, created = UserVideoProgress.objects.get_or_create(
                user=request.user,
                video=video,
                defaults={'is_watched': True}
            )
            
            if not created:
                progress.is_watched = True
                progress.save()
            
            # Check if chapter is now completed and update progress
            chapter = video.chapter
            if chapter:
                total_videos_in_chapter = CourseVideoForOrderedUser.objects.filter(chapter=chapter).count()
                watched_videos_in_chapter = UserVideoProgress.objects.filter(
                    user=request.user,
                    video__chapter=chapter,
                    is_watched=True
                ).count()
                
                chapter_completed = total_videos_in_chapter > 0 and watched_videos_in_chapter == total_videos_in_chapter
                
                if chapter_completed:
                    chapter_progress, created = UserChapterProgress.objects.get_or_create(
                        user=request.user,
                        chapter=chapter,
                        defaults={'is_completed': True, 'completed_at': timezone.now()}
                    )
                    if not created and not chapter_progress.is_completed:
                        chapter_progress.is_completed = True
                        chapter_progress.completed_at = timezone.now()
                        chapter_progress.save()
            
            # Calculate new progress
            order = video.order
            all_videos = CourseVideoForOrderedUser.objects.filter(order=order, is_accessible=True)
            watched_videos = UserVideoProgress.objects.filter(
                user=request.user,
                video__in=all_videos,
                is_watched=True
            ).count()
            
            total_videos = all_videos.count()
            
            # Check if course has a quiz and if it's passed
            has_quiz = False
            quiz_passed = False
            try:
                quiz = CourseQuiz.objects.get(course=order.course, is_active=True)
                has_quiz = True
                quiz_attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-started_at').first()
                if quiz_attempt:
                    quiz_passed = quiz_attempt.is_passed
            except CourseQuiz.DoesNotExist:
                pass
            
            # Calculate progress percentage based on video completion and quiz status
            if total_videos > 0:
                video_progress = (watched_videos / total_videos * 100)
                
                if has_quiz:
                    # If course has quiz, max progress is 90% until quiz is passed
                    if quiz_passed:
                        progress_percentage = 100  # 100% only after passing quiz
                    else:
                        progress_percentage = min(90, video_progress)  # Max 90% for video completion
                else:
                    # If no quiz, progress is based on video completion only
                    progress_percentage = video_progress
            else:
                progress_percentage = 0
            
            return JsonResponse({
                'success': True,
                'message': 'Video marked as watched',
                'progress': {
                    'watched_videos': watched_videos,
                    'total_videos': total_videos,
                    'percentage': round(progress_percentage, 1),
                    'is_completed': progress_percentage >= 100
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# Quiz Views
@login_required
def start_quiz(request, course_id):
    """Start quiz for a course"""
    course = get_object_or_404(Courses, id=course_id)
    
    # Check if user has access to the course (same logic as course_results)
    orders = CourseOrder.objects.filter(user=request.user, course=course, is_active=True)
    
    if not orders.exists():
        messages.error(request, 'У вас нет доступа к этому курсу')
        return redirect('courses:my_courses')
    
    # Check if course has a quiz
    try:
        quiz = CourseQuiz.objects.get(course=course, is_active=True)
    except CourseQuiz.DoesNotExist:
        messages.error(request, 'Для этого курса тест не создан')
        return redirect('courses:my_courses')
    
    # Check if user already passed the quiz
    if QuizAttempt.objects.filter(user=request.user, quiz=quiz, is_passed=True).exists():
        messages.info(request, 'Вы уже прошли этот тест')
        return redirect('courses:quiz_results', course_id=course_id)
    
    # Get random questions
    questions = quiz.get_random_questions()
    
    if not questions:
        messages.error(request, 'В тесте нет вопросов')
        return redirect('courses:my_courses')
    
    
    # Create new quiz attempt (allow multiple attempts until passed)
    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
        answers={}
    )
    
    context = {
        'course': course,
        'quiz': quiz,
        'questions': questions,
        'attempt': attempt,
    }
    
    return render(request, 'quiz/quiz.html', context)


@login_required
def submit_quiz(request, course_id):
    """Submit quiz answers"""
    if request.method != 'POST':
        messages.error(request, 'Неверный метод запроса')
        return redirect('courses:my_courses')
    
    course = get_object_or_404(Courses, id=course_id)
    
    # Check if user has access to the course
    orders = CourseOrder.objects.filter(user=request.user, course=course, is_active=True)
    if not orders.exists():
        messages.error(request, 'У вас нет доступа к этому курсу')
        return redirect('courses:my_courses')
    
    try:
        quiz = CourseQuiz.objects.get(course=course, is_active=True)
        # Get the latest attempt (most recent one)
        attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-started_at').first()
        if not attempt:
            messages.error(request, 'Попытка теста не найдена')
            return redirect('courses:my_courses')
    except CourseQuiz.DoesNotExist:
        messages.error(request, 'Тест не найден')
        return redirect('courses:my_courses')
    
    if attempt.is_completed:
        messages.info(request, 'Вы уже прошли этот тест')
        return redirect('courses:quiz_results', course_id=course_id)
    
    try:
        # Get answers from request
        answers = {}
        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = key.replace('question_', '')
                answers[question_id] = value
        
        # Update attempt with answers
        attempt.answers = answers
        attempt.is_completed = True
        attempt.completed_at = timezone.now()
        
        # Calculate time taken
        if attempt.started_at:
            time_taken = (attempt.completed_at - attempt.started_at).total_seconds()
            attempt.time_taken = int(time_taken)
        
        # Calculate score
        score, percentage = attempt.calculate_score()
        
        # Create certificate if passed
        if attempt.is_passed:
            certificate, created = QuizCertificate.objects.get_or_create(
                user=request.user,
                quiz=quiz,
                defaults={'attempt': attempt}
            )
            messages.success(request, f'Поздравляем! Вы прошли тест с результатом {percentage:.1f}%')
        else:
            messages.warning(request, f'Тест не пройден. Ваш результат: {percentage:.1f}%. Для прохождения необходимо набрать {quiz.passing_score}%')
        
        # Redirect to results page
        return redirect('courses:quiz_results', course_id=course_id)
        
    except Exception as e:
        messages.error(request, f'Ошибка при обработке теста: {str(e)}')
        return redirect('courses:my_courses')


@login_required
def quiz_results(request, course_id):
    """Show quiz results"""
    course = get_object_or_404(Courses, id=course_id)
    
    # Check if user has access to the course
    orders = CourseOrder.objects.filter(user=request.user, course=course, is_active=True)
    if not orders.exists():
        messages.error(request, 'У вас нет доступа к этому курсу')
        return redirect('courses:my_courses')
    
    try:
        quiz = CourseQuiz.objects.get(course=course, is_active=True)
        # Get the latest attempt (most recent one)
        attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-started_at').first()
        if not attempt:
            messages.error(request, 'Результаты теста не найдены')
            return redirect('courses:my_courses')
    except CourseQuiz.DoesNotExist:
        messages.error(request, 'Тест не найден')
        return redirect('courses:my_courses')
    
    # Get certificate if exists
    certificate = None
    if attempt.is_passed:
        try:
            certificate = QuizCertificate.objects.get(user=request.user, quiz=quiz)
        except QuizCertificate.DoesNotExist:
            pass
    
    # Get questions with correct answers for review
    questions = QuizQuestion.objects.filter(quiz=quiz, id__in=attempt.answers.keys())
    
    context = {
        'course': course,
        'quiz': quiz,
        'attempt': attempt,
        'certificate': certificate,
        'questions': questions,
    }
    
    return render(request, 'quiz/quiz_results.html', context)


@login_required
def quiz_certificate(request, course_id):
    """Download quiz certificate"""
    course = get_object_or_404(Courses, id=course_id)
    
    # Check if user has access to the course
    orders = CourseOrder.objects.filter(user=request.user, course=course, is_active=True)
    if not orders.exists():
        messages.error(request, 'У вас нет доступа к этому курсу')
        return redirect('courses:my_courses')
    
    try:
        quiz = CourseQuiz.objects.get(course=course, is_active=True)
        certificate = QuizCertificate.objects.get(user=request.user, quiz=quiz, is_active=True)
    except (CourseQuiz.DoesNotExist, QuizCertificate.DoesNotExist):
        messages.error(request, 'Сертификат не найден')
        return redirect('courses:my_courses')
    
    # For now, just show certificate info
    # In a real implementation, you would generate a PDF certificate
    context = {
        'course': course,
        'quiz': quiz,
        'certificate': certificate,
        'attempt': certificate.attempt,
    }
    
    return render(request, 'quiz/certificate.html', context)


@login_required
def quiz_dashboard(request):
    """Quiz dashboard showing all user's quiz attempts"""
    # Get all quiz attempts for the user
    quiz_attempts = QuizAttempt.objects.filter(
        user=request.user,
        is_completed=True
    ).select_related('quiz', 'quiz__course').order_by('-completed_at')
    
    context = {
        'quiz_attempts': quiz_attempts,
    }
    
    return render(request, 'quiz/quiz_dashboard.html', context)
