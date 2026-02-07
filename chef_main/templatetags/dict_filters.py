# chef_main/templatetags/dict_filters.py
from django import template

register = template.Library()



@register.filter
def get_dict_value(dictionary, key):
    """Альтернативное название для фильтра"""
    return get_item(dictionary, key)


@register.filter
def get_item(dictionary, key):
    """Получение значения из словаря по ключу"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter(name='has_key')
def has_key(dictionary, key):
    """Проверка наличия ключа в словаре"""
    if isinstance(dictionary, dict):
        return key in dictionary
    return False

@register.filter
def to_kg(value):
    """Преобразование граммов в килограммы для отображения"""
    try:
        grams = float(value)
    except (TypeError, ValueError):
        return 0
    return grams / 1000.0
