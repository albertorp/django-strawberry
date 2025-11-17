from django.shortcuts import render

# Create your views here.
from strawberry.views import BaseCrudView, UserBaseCrudView
from .models import Book, SampleModel, Country
from .tables import BookTable, SampleModelTable, CountryTable



class BookView(BaseCrudView):
    model = Book
    fields = ("title", "author")

    table_class = BookTable

    allow_delete = True
    allow_delete_multiple = True
    allow_delete_all = True
    allow_multiselect = False




class CountryView(BaseCrudView):
    model = Country
    fields = ["name", "iso_code"]
    allow_delete = True
    allow_delete_multiple = True
    allow_delete_all = True
    allow_multiselect = False

    table_class = CountryTable



class SampleModelView(UserBaseCrudView):
    model = SampleModel
    # fields = ['name', 'date', 'email', 'status', 'active', 'country', 'user']
    fields = "__all__"
    detail_fields = ['name', 'date', 'email', 'phone', 'active', 'user']
    # form_fields = ['name', 'date', 'user']
    filter_fields = ['name', 'date', 'active',]

    # filterset_class = SampleFilter
    # form_multiselect_class = SampleModelChangeMultipleForm

    allow_delete = True
    allow_delete_multiple = True
    allow_delete_all = True
    allow_multiselect = False
    # allow_filter = False

    table_class = SampleModelTable