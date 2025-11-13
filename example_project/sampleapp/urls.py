from django.urls import path
from .views import *

urlpatterns = BookView.get_urls()