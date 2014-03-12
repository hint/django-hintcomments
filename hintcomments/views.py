from django.contrib.comments.models import Comment
from django.contrib import comments
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.comments.views.comments import post_comment, CommentPostBadRequest
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.html import escape
from hintcomments.http import FormInvalidResponse
from django.contrib.comments import signals
import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.utils.timesince import timesince
from django.core.cache import cache
from hintcomments import app_settings
from ipware.ip import get_real_ip
from django.utils.html import escape


FIELDS = ('id', 'comment', 'submit_date', 'user_name', 'content_type', 'object_pk')


def ajax_post_comment(request, next=None, using=None):
    if request.is_ajax():
        ctype = request.POST.get("content_type")
        object_pk = request.POST.get("object_pk")
        ip = get_real_ip(request)
        captcha = False
        if ip:
            comments_count = cache.get('comments_count_for_%s' % ip, 0)
            if comments_count >= app_settings.MAX_INSTANT_COMMENTS:
                captcha = True
        if ctype is None or object_pk is None:
            return CommentPostBadRequest("Missing content_type or object_pk field.")
        try:
            model = models.get_model(*ctype.split(".", 1))
            target = model._default_manager.using(using).get(pk=object_pk)
        except TypeError:
            return CommentPostBadRequest(
                "Invalid content_type value: %r" % escape(ctype))
        except AttributeError:
            return CommentPostBadRequest(
                "The given content-type %r does not resolve to a valid model." %
                escape(ctype))
        except ObjectDoesNotExist:
            return CommentPostBadRequest(
                "No object matching content-type %r and object PK %r exists." %
                (escape(ctype), escape(object_pk)))
        except (ValueError, ValidationError), e:
            return CommentPostBadRequest(
                "Attempting go get content-type %r and object PK %r exists raised %s" %
                (escape(ctype), escape(object_pk), e.__class__.__name__))

        form_template_list = [
            "comments/%s/%s/form.html" % (model._meta.app_label, model._meta.module_name),
            "comments/%s/form.html" % model._meta.app_label,
            "comments/form.html",
        ]

        # Construct the comment form
        form = comments.get_form()(target, data=request.POST, captcha=captcha)

        # Check security information
        if form.security_errors():
            return FormInvalidResponse(form_template_list, form)

        if form.errors:  # or preview:
            return FormInvalidResponse(form_template_list, form)
#            return HttpResponseBadRequest('<script type="text/javascript">alert("Ujjj zlllee");</script>')

        # Otherwise create the comment
        comment = form.get_comment_object()
        comment.ip_address = request.META.get("REMOTE_ADDR", None)
        if request.user.is_authenticated():
            comment.user = request.user

        # Signal that the comment is about to be saved
        responses = signals.comment_will_be_posted.send(sender=comment.__class__, comment=comment, request=request)

        for (receiver, response) in responses:
            if response==False:
                return FormInvalidResponse(form_template_list, form, extra_errors=[_('Comment has been rejected')])

        # Save the comment and signal that it was saved
        comment.save()
        if ip:
            if captcha:  # captcha was provided correclty reset comment count
                comments_count = 0
            else:
                comments_count += 1
            cache.set('comments_count_for_%s' % ip, comments_count, app_settings.COMMENTS_COOLDOWN)

        signals.comment_was_posted.send(sender=comment.__class__, comment=comment, request=request)

        comment = model_to_dict(comment, fields=FIELDS)

        _prepare_comments([comment])

        return HttpResponse(json.dumps(comment, cls=DjangoJSONEncoder), content_type="application/json")
    else:
        # go the default django path
        return post_comment(request, next=next, using=using)


def _prepare_comments(comments):
    for comment in comments:
        comment['user_name'] = escape(comment['user_name'])
        comment['comment'] = escape(comment['comment'])
        comment['timesince'] = timesince(comment['submit_date'])
    return comments


def comment_list(request, content_type_id, object_pk, last_comment_id=None):
    limit = 31  # this is also hardcoded in JavaScript
    comments = Comment.objects.filter(content_type__id=content_type_id, object_pk=object_pk)
    if last_comment_id:
        comments = comments.filter(id__lt=last_comment_id)
    comments = comments.values(*FIELDS).order_by('-submit_date')[:limit]
    _prepare_comments(comments)
    return HttpResponse(json.dumps(list(comments), cls=DjangoJSONEncoder), content_type="application/json")
