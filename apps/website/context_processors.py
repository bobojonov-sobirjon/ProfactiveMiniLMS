from .models import FAQ

def faq_context(request):
    """Add FAQ context to all templates"""
    return {
        'faqs': FAQ.objects.filter(is_active=True).order_by('order', 'created_at')
    }