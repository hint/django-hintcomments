from django.conf.urls.defaults import *

from django.contrib.comments.urls import urlpatterns as comment_urls

urlpatterns = patterns('',
    url(r'^post/$',          'hintcomments.views.ajax_post_comment',                  name='comments-post-comment'),
    url(r'^posted/$',        'django.contrib.comments.views.comments.comment_done',   name='comments-comment-done'),
    url(r'^flag/(\d+)/$',    'django.contrib.comments.views.moderation.flag',         name='comments-flag'),
    url(r'^flagged/$',       'django.contrib.comments.views.moderation.flag_done',    name='comments-flag-done'),
    url(r'^delete/(\d+)/$',  'django.contrib.comments.views.moderation.delete',       name='comments-delete'),
    url(r'^deleted/$',       'django.contrib.comments.views.moderation.delete_done',  name='comments-delete-done'),
    url(r'^approve/(\d+)/$', 'django.contrib.comments.views.moderation.approve',      name='comments-approve'),
    url(r'^approved/$',      'django.contrib.comments.views.moderation.approve_done', name='comments-approve-done'),
    url(r'^comments/(?P<content_type_id>\d+)/(?P<object_pk>\d+)/(?P<last_comment_id>\d*)$', 'hintcomments.views.comment_list', name='comments-list')
)

urlpatterns += comment_urls
