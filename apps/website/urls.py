from django.urls import path, include
from apps.website import views
from apps.courses import views as courses_views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('course-catalogue/', views.course_catalogue, name='course-catalogue'),
    path('materials/', views.materials, name='materials'),
    path('popular/', views.popular, name='popular'),
    path('referal/', views.referal, name='referal'),
    path('referal-request/', views.referal_request, name='referal_request'),
    path('referral/<str:promo_code>/', views.referral_redirect, name='referral_redirect'),
    path('contacts/', views.contacts, name='contacts'),
    path('documentation/', views.documentation, name='documentation'),
    path('documents/', views.documents_page, name='documents'),
    path('download/<int:document_id>/', views.download_document, name='download_document'),
    path('download-privacy-policy/', views.download_privacy_policy, name='download_privacy_policy'),
    path('faq/', views.get_faqs, name='faq'),
    path('blog/', views.blog, name='blog'),
    path('reviews/', courses_views.reviews_page, name='reviews'),
    path('courses/', include('apps.courses.urls')),
]