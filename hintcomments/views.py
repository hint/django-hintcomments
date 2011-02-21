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


def ajax_post_comment(request, next=None, using=None):
    assert(isinstance(request, HttpRequest)) #todo remove this - usefull in my IDE ;)
    if request.is_ajax():
        response = post_comment(request, next=next, using=using) # todo: this is temporary hack - must write own view
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
                "The given content-type %r does not resolve to a valid model." % \
                    escape(ctype))
        except ObjectDoesNotExist:
            return CommentPostBadRequest(
                "No object matching content-type %r and object PK %r exists." % \
                    (escape(ctype), escape(object_pk)))
        except (ValueError, ValidationError), e:
            return CommentPostBadRequest(
                "Attempting go get content-type %r and object PK %r exists raised %s" % \
                    (escape(ctype), escape(object_pk), e.__class__.__name__))

        # Construct the comment form
        form = comments.get_form()(target, data=data)

        # Check security information
        if form.security_errors():
            return CommentPostBadRequest(
                "The comment form failed security verification: %s" % \
                    escape(str(form.security_errors())))

        if form.errors:# or preview:
            # todo: perform error checking
            pass

        comment_list = Comment.objects.for_model(model).order_by("submit_date")

        template_list = [
                "comments/%s/%s/list.html" % (model._meta.app_label, model._meta.module_name),
                "comments/%s/list.html" % model._meta.app_label,
                "comments/list.html",
                ]

        return render_to_response(
            template_list, {
                "comment_list": comment_list,
                },
            RequestContext(request, {})
        )
    else:
        # go the default django path
        return post_comment(request, next=next, using=using)
