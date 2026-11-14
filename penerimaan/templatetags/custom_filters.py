# custom_filters.py
from decimal import Decimal
from django import template

register = template.Library()

@register.filter
def get_subtotal(subtotal_list, dana):
    for item in subtotal_list:
        if item['dana'] == dana:
            return item['subtotal']
    return 0

@register.filter
def unlocalize(value):
    """Return the value unformatted"""
    return str(value)

@register.filter
def rupiah(value):
    """Format angka menjadi format mata uang Indonesia dengan 2 desimal"""
    if value is None or value == "":
        return "0,00"
    try:
        val = Decimal(str(value))
        return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(value)

# @register.filter
# def zip_lists(list1, list2):
#     """Menggabungkan dua list menjadi iterator tuple pasangan."""
#     return zip(list1, list2)