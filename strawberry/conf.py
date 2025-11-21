# strawberry/conf.py
from django.conf import settings

UI = getattr(settings, "STRAWBERRY_UI", "default")

