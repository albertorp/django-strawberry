from django.shortcuts import render

# Create your views here.
from strawberry.views import BaseCrudView
from .models import Book
from .tables import BookTable

class BookView(BaseCrudView):
    model = Book
    fields = ("title", "author")

    table_class = BookTable

    allow_delete = True
    allow_delete_multiple = True
    allow_delete_all = True
    allow_multiselect = False
