from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    return dictionary.get(key)

@register.filter
def get_attribute(obj, attr):
    """Get an attribute from an object by name"""
    return getattr(obj, attr, None)

@register.filter
def subtract(value, arg):
    """Subtracts the arg from the value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value 