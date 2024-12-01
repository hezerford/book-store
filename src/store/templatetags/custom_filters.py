from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def truncate_description(description, max_length):
    if len(description) > max_length:
        return description[:max_length] + "..."
    return description