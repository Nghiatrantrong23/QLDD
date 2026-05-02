"""
Custom template tags for myapp
"""
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Thay thế hoặc thêm tham số vào query string hiện tại.
    Dùng để giữ các tham số tìm kiếm khi chuyển trang.
    
    Usage: {% param_replace trang=2 %}
    """
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    # Remove empty parameters
    for k in list(query.keys()):
        if query[k] == '' or query[k] is None:
            del query[k]
    return query.urlencode()
