from .models import FAQ, DiscountForReferral

def faq_context(request):
    """Add FAQ context to all templates"""
    return {
        'faqs': FAQ.objects.filter(is_active=True).order_by('order', 'created_at')
    }

def discount_context(request):
    """Add discount context to all templates"""
    discount = DiscountForReferral.get_active_discount()
    return {
        'referral_discount': discount
    }