from django.utils.html import format_html
from django.template.loader import render_to_string

import django_tables2 as tables

import itertools

from strawberry.tables import BaseTable

from .models import Book, SampleModel, Country

class BookTable(BaseTable):

    class Meta(BaseTable.Meta):
        model = Book
        fields = ("title", "author", )



class CountryTable(BaseTable):

    class Meta(BaseTable.Meta):
        model = Country
        fields = ("name", "iso_code", )


class SampleModelTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = SampleModel
        fields = ['name', 'date', 'email', 'status', 'active', 'country']


    def render_name(self, value, record):
        context = {
            'value': value,
            'record': record
        }
        return render_to_string('sampleapp/partial/columns/name.html', context=context)
