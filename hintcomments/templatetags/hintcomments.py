# -*- coding: utf-8 -*-

from __future__ import absolute_import  # fixes: from hintcomments import app_settings
from django.contrib.comments.templatetags import comments as _comments
from django.contrib.comments.models import Comment
from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import safe
from django.utils.safestring import mark_safe
from ipware.ip import get_ip as get_real_ip
from django.core.cache import cache
from hintcomments import app_settings

register = template.Library()

DEFAULT_PAGINATION_SETTINGS={
            'current_page'          : 0,
            'items_per_page'        : 10,
            'link_to'               : '#',
            'num_display_entries'   : 11,
            'next_text'             : 'Next',
            'next_show_always'      : True,
            'prev_text'             : 'Previous',
            'prev_show_always'      : True,
            'num_edge_entries'      : 0,
            'ellipse_text'          : '...',
            }

class AjaxPaginationNode(template.Node):
    def __init__(self, comments_selector, **kwargs):
        self.settings = DEFAULT_PAGINATION_SETTINGS
        self.settings.update({'comments_selector' : comments_selector})
        self.settings.update(kwargs)
        
        param = '<input type="hidden" name="%(key)s" value="%(value)s"/>'
        self.opts = [param % {'key':key, 'value':value} for key, value in self.settings.items()]

    def render(self, context):
        try:
            return mark_safe('<div class="pagination-container"></div>%s' % ''.join(self.opts))
        except template.VariableDoesNotExist:
            return ''

def ajax_comment_pagination(parser, token):
    try:
        tag = token.split_contents()[0]
        comments_selector = token.split_contents()[1][1:-1] #don't forget to strip off string markers
        kwargs = token.split_contents()[2:]
        kwargs = dict([arg.replace(" ","").split("=") for arg in kwargs])
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly one positional argument" % token.contents.split()[0]
    
    if kwargs and not all([key in DEFAULT_PAGINATION_SETTINGS for key in kwargs.keys()]):
        raise template.TemplateSyntaxError, "%r tag accepts only one of those keyword arguments %s" % \
                                            (token.contents.split()[0],", ".join(DEFAULT_PAGINATION_SETTINGS.keys()))

    return AjaxPaginationNode(comments_selector, **kwargs)


class RenderCommentFormNode(_comments.RenderCommentFormNode):
    def get_form(self, context):
        ip = get_real_ip(context['request'])
        captcha = False
        if ip:
            comments_count = cache.get('comments_count_for_%s' % ip, 0)
            print '>>> comments_count', comments_count
            if comments_count >= app_settings.MAX_INSTANT_COMMENTS:
                captcha = True
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            return _comments.comments.get_form()(ctype.get_object_for_this_type(pk=object_pk), captcha=captcha)
        else:
            return None


class RenderAjaxCommentListNode(_comments.RenderCommentListNode):
    def render(self, context):
        return mark_safe(
            '<div id="ajax-comment-list-holder">%s</div>' % super(RenderAjaxCommentListNode, self).render(context))


def render_comment_list(parser, token):
    return RenderAjaxCommentListNode.handle_token(parser, token)


def render_comment_form(parser, token):
    return RenderCommentFormNode.handle_token(parser, token)


register.tag(_comments.get_comment_count)
register.tag(_comments.get_comment_list)
register.tag(_comments.get_comment_form)
register.tag(render_comment_form)
register.tag(render_comment_list)
register.tag(ajax_comment_pagination)
register.simple_tag(_comments.comment_form_target)
register.simple_tag(_comments.get_comment_permalink)
