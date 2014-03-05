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

FIELDS = ('id', 'comment', 'submit_date', 'user_name', 'content_type', 'object_pk')


def ajax_post_comment(request, next=None, using=None):
    if request.is_ajax():
        # Fill out some initial data fields from an authenticated user, if present
        data = request.POST.copy()
        if request.user.is_authenticated():
            if not data.get('name', ''):
                data["name"] = request.user.get_full_name() or request.user.username
            if not data.get('email', ''):
                data["email"] = request.user.email

        ctype = data.get("content_type")
        object_pk = data.get("object_pk")
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
        form = comments.get_form()(target, data=data)

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
        signals.comment_was_posted.send(sender=comment.__class__, comment=comment, request=request)

        comment = model_to_dict(comment, fields=FIELDS)

        _add_timesince([comment])

        return HttpResponse(json.dumps(comment, cls=DjangoJSONEncoder), content_type="application/json")
    else:
        # go the default django path
        return post_comment(request, next=next, using=using)


def _add_timesince(comments):
    for comment in comments:
        comment['timesince'] = timesince(comment['submit_date'])
    return comments


def comment_list(request, content_type_id, object_pk, last_comment_id=None):
    limit = 31  # this is also hardcoded in JavaScript
    comments = Comment.objects.filter(content_type__id=content_type_id, object_pk=object_pk)
    if last_comment_id:
        comments = comments.filter(id__lt=last_comment_id)
    comments = comments.values(*FIELDS).order_by('-submit_date')[:limit]
    _add_timesince(comments)
    return HttpResponse(json.dumps(list(comments), cls=DjangoJSONEncoder), content_type="application/json")
