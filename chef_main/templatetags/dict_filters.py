# chef_main/templatetags/dict_filters.py
from django import template

register = template.Library()



@register.filter
def get_dict_value(dictionary, key):
    return get_item(dictionary, key)


@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter(name='has_key')
def has_key(dictionary, key):
    if isinstance(dictionary, dict):
        return key in dictionary
    return False

@register.filter
def to_kg(value):
    try:
        grams = float(value)
    except (TypeError, ValueError):
        return 0
    return grams / 1000.0
