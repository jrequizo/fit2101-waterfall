from django import template
register = template.Library()


@register.filter
def i(indexable, i):
    return indexable[i]