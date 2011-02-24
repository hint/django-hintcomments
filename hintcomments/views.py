from functools import wraps
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib import comments
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseBadRequest, HttpRequest
from django.contrib.comments.views.comments import post_comment, CommentPostBadRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.db import models
from django.utils.html import escape
from multikino.hintcomments.http import FormInvalidResponse
from django.contrib.comments import signals


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
                "The given content-type %r does not resolve to a valid model." %\
                escape(ctype))
        except ObjectDoesNotExist:
            return CommentPostBadRequest(
                "No object matching content-type %r and object PK %r exists." %\
                (escape(ctype), escape(object_pk)))
        except (ValueError, ValidationError), e:
            return CommentPostBadRequest(
                "Attempting go get content-type %r and object PK %r exists raised %s" %\
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
            return FormInvalidResponse(form_template_list,form)

        if form.errors:# or preview:
            return FormInvalidResponse(form_template_list,form)
#            return HttpResponseBadRequest('<script type="text/javascript">alert("Ujjj zlllee");</script>')

        # Otherwise create the comment
        comment = form.get_comment_object()
        comment.ip_address = request.META.get("REMOTE_ADDR", None)
        if request.user.is_authenticated():
            comment.user = request.user

        # Signal that the comment is about to be saved
        responses = signals.comment_will_be_posted.send(
            sender  = comment.__class__,
            comment = comment,
            request = request
        )

        for (receiver, response) in responses:
            if response == False:
                return CommentPostBadRequest(
                    "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

        # Save the comment and signal that it was saved
        comment.save()
        signals.comment_was_posted.send(
            sender  = comment.__class__,
            comment = comment,
            request = request
        )

        comment_list = Comment.objects.for_model(model).filter(object_pk=object_pk).order_by("submit_date")

        template_list = [
                "comments/%s/%s/list.html" % (model._meta.app_label, model._meta.module_name),
                "comments/%s/list.html" % model._meta.app_label,
                "comments/list.html",
                ]
        print "up to the end"
        return render_to_response(
            template_list, {
                "comment_list": comment_list,
                },
            RequestContext(request, {})
        )
    else:
        # go the default django path
        return post_comment(request, next=next, using=using)
