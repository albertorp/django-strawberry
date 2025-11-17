from django.urls import path
from . import views

urlpatterns = views.BookView.get_urls()
urlpatterns += views.CountryView.get_urls()
urlpatterns += views.SampleModelView.get_urls()