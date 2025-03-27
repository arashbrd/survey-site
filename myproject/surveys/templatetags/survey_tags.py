from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary using a key.
    Returns None if the key doesn't exist or if the input is not a dictionary.
    """
    if isinstance(dictionary, dict):
        return dictionary.get(str(key))
    return None 