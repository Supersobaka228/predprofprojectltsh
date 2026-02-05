# chef_main/templatetags/dict_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Получение значения из словаря по ключу.
    Использование в шаблоне: {{ dictionary|get_item:key }}
    """
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def get_dict_value(dictionary, key):
    """Альтернативное название для фильтра"""
    return get_item(dictionary, key)