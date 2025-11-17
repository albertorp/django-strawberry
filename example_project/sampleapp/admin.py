from django.contrib import admin

# Register your models here.
from .models import SampleModel, Country, Book

class SampleModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date', 'status', 'active', 'user')
    list_filter = ('status', 'active', 'user')
    search_fields = ('name', 'description')
    date_hierarchy = 'date'

admin.site.register(SampleModel, SampleModelAdmin)

admin.site.register(Country)

admin.site.register(Book)
