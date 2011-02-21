django-hintcomments
============================

This project is a modification of django comments framework that enables it to use AJAX for committing and updating
comments.
The goal is to introduce a solution that will allow quick and painless change form django default comment framework
to hintcomments.


Features:
---------

1. Commit comments using AJAX

Installation:
-------------

* Put ``hintcomments`` in your ``INSTALLED_APPS``
* Put ``django.contrib.comments`` in your ``INSTALLED_APPS`` (in that order)
* include jQuery 1.4.2 or greater
* include ``media/js/hintcomments.js`` in your media

Usage:
------

All you need to do is substitute all {% load comments %} with {% load hintcomments %} and attach ``hintCommentForm`` on
all forms that commit a comment.   
