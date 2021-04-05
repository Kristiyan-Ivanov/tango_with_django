from django import template
from rango.models import Category, Page

register = template.Library()


@register.inclusion_tag('rango/categories.html')
def get_category_list(current_category=None):
    return {'categories': Category.objects.all(),
            'current_category': current_category}


@register.inclusion_tag('rango/list_pages.html')
def get_pages_list(category_id):
    return {'pages': Page.objects.filter(category_id=category_id).order_by('-views')}
