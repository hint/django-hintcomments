from django.conf import settings

COMMENTS_COOLDOWN = getattr(settings, 'HINTCOMMENTS_COMMENTS_COOLDOWN', 60 * 10)
MAX_INSTANT_COMMENTS = getattr(settings, 'HINTCOMMENTS_MAX_INSTANT_COMMENTS', 2)
