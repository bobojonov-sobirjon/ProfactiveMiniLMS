from django import template
from apps.order.models import UserVideoProgress

register = template.Library()

@register.simple_tag
def is_video_watched(video_id, user):
    """Check if a video is watched by the user"""
    if not user or not user.is_authenticated:
        return False
    
    return UserVideoProgress.objects.filter(
        user=user,
        video_id=video_id,
        is_watched=True
    ).exists()
