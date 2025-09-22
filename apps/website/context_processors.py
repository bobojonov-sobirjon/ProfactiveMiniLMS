from .models import FAQ, DiscountForReferral, MainHeader

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

def main_header_context(request):
    """Add main header context to all templates"""
    main_header = MainHeader.get_active_header()
    return {
        'main_header': main_header
    }