from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_catalogue, name='course_catalogue'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('course-results/', views.course_results, name='course_results'),
    path('ordered-course/<int:order_id>/', views.ordered_course_detail, name='ordered_course_detail'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('popular/', views.popular_courses, name='popular_courses'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('get-access/<int:course_id>/', views.get_access, name='get_access'),
    path('create-order/<int:course_id>/', views.create_course_order, name='create_order'),
    path('mark-video-watched/', views.mark_video_watched, name='mark_video_watched'),
    path('api/subcategories/', views.get_subcategories, name='get_subcategories'),
    path('create-review/<int:course_id>/', views.create_course_review, name='create_review'),
    path('reviews/', views.reviews_page, name='reviews'),
    # Quiz URLs
    path('quiz/<int:course_id>/start/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:course_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('quiz/<int:course_id>/results/', views.quiz_results, name='quiz_results'),
    path('quiz/<int:course_id>/certificate/', views.quiz_certificate, name='quiz_certificate'),
]
