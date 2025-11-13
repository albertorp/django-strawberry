from django.utils.html import format_html
from django.template.loader import render_to_string

import django_tables2 as tables

import itertools

from strawberry.tables import BaseTable

from .models import Book

class BookTable(BaseTable):

    class Meta(BaseTable.Meta):
        model = Book
        fields = ("title", "author", )