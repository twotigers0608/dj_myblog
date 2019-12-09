# -*- coding:utf8 -*-

from django import template
from ..models import Post, Category, Tag

register = template.Library()


@register.inclusion_tag('index.html', takes_context=True)
def show_recent_posts(context, num=5):
    return {
        'recent_post_list': Post.objects.all().order_by('-created_time')[:num],
    }
