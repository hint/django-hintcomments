# -*- coding: utf-8 -*-

from django.contrib.comments.templatetags import comments as _comments
from django.contrib.comments.models import Comment
from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import safe
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_comment_here(object):
    ctype = ContentType.objects.get_for_model(object)
    comments = Comment.objects.filter(content_type=ctype, object_pk=object.pk).order_by("-submit_date")
    try:
        last_comment = comments[0].pk
    except IndexError:
        last_comment = ""
    return safe('<input type="hidden" name="last_comment_pk" value="%s"/>' % last_comment)

@register.simple_tag
def ajax_comment_pagination(comments_selector, paginate_by=5):
    opts = []
    opts.append('<input type="hidden" name="%s" value="%s"/>' % ('comments_selector', comments_selector))
    opts.append('<input type="hidden" name="%s" value="%s"/>' % ('paginate_by', paginate_by))
    return mark_safe('<div class="pagination-container"></div>%s' % ''.join(opts))

def render_comment_list(parser, token, element_id="comment-list-holder"):
    return RenderAjaxCommentListNode.handle_token(parser, token)

class RenderAjaxCommentListNode(_comments.RenderCommentListNode):
    def render(self, context):
        return mark_safe('<div id="ajax-comment-list-holder">%s</div>' % super(RenderAjaxCommentListNode, self).render(context))

register.tag(_comments.get_comment_count)
register.tag(_comments.get_comment_list)
register.tag(_comments.get_comment_form)
register.tag(_comments.render_comment_form)
register.tag(render_comment_list)
register.simple_tag(_comments.comment_form_target)
register.simple_tag(_comments.get_comment_permalink)
