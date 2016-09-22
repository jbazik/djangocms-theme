from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def theme(context):
    try:
        page = context['request'].current_page
        while page and not hasattr(page, 'pagetheme'):
            page = page.parent
        return mark_safe("\n".join([
            '<link rel="stylesheet" type="text/css" href="%s" media="%s">' %
                   (url, media) for url, media in
                   page.pagetheme.theme.stylesheet_links()]))
    except AttributeError:
        return ''
