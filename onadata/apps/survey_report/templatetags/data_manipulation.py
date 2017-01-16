from django import template

register = template.Library()

@register.filter
def index(l, i):
    try:
        return l[i]
    except:
        return None
        
@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def fsmedia(data_list):
    if isinstance(data_list[-1], list):
        return data_list[-1]
    elif isinstance(data_list[-2], list):
        return data_list[-2]
    return []


