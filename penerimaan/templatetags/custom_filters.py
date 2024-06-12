# custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_subtotal(subtotal_list, dana):
    for item in subtotal_list:
        if item['dana'] == dana:
            return item['subtotal']
    return 0
