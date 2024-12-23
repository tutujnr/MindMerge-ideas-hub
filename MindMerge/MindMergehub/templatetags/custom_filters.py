from django import template
from datetime import timedelta, datetime
from django.utils import timezone
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def human_readable_date(value):
    """
    Custom template filter to generate human-readable datetime representation.
    
    Args:
        value (datetime or str): Input datetime object or ISO-formatted datetime string
    
    Returns:
        str: Humanized time representation
    
    Key Considerations:
    - Handles timezone-aware and naive datetime objects
    - Provides contextual time representations
    - Implements granular time difference categorization
    """
    # Type and Timezone Normalization
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value

    # Timezone Awareness Handling
    if not timezone.is_aware(value):
        value = timezone.make_aware(value)
    
    value = timezone.localtime(value)
    current_time = timezone.now()
    time_difference = current_time - value

    # Comprehensive Time Representation Logic
    if time_difference.days > 7:
        # For dates older than a week, return formatted date
        return value.strftime('%b %d')
    elif time_difference.days > 1:
        # For dates within last week, return day of week
        return value.strftime('%a')
    elif time_difference.days == 1:
        return "Yesterday"
    elif time_difference.days == 0:
        if time_difference.seconds >= 3600:
            # Hours ago
            hours = time_difference.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif time_difference.seconds >= 60:
            # Minutes ago
            minutes = time_difference.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            # Recent moments
            return "Just now"
    
    return value.strftime('%b %d')