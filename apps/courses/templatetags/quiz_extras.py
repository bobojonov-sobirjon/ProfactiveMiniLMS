from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key, handling int/str key mismatches"""
    if dictionary is None:
        return None
    # Exact key
    if key in dictionary:
        return dictionary.get(key)
    # Stringified key (common when JSONField stores keys as strings)
    str_key = str(key)
    if str_key in dictionary:
        return dictionary.get(str_key)
    # Integer key fallback
    try:
        int_key = int(key)
        if int_key in dictionary:
            return dictionary.get(int_key)
    except (ValueError, TypeError):
        pass
    return None
