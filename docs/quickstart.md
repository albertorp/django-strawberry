# Quickstart

A minimal setup to get a CRUD screen running with Strawberry + Neapolitan + django-tables2.

## 1. Define a model
```python
# myapp/models.py
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title
```

## 2. Create a CRUD view
```python
# myapp/views.py
from strawberry.views import BaseCrudView
from .models import Book

class BookView(BaseCrudView):
    model = Book
    fields = ("title", "author")  # fields for list/detail/form

    allow_delete = True
    allow_delete_multiple = True
    allow_delete_all = True
```
Strawberry will auto-build a ModelForm and a django-tables2 table if you do not supply your own classes.

## 3. Wire up URLs
```python
# myapp/urls.py
from django.urls import path
from .views import BookView

urlpatterns = BookView.get_urls()  # includes list/detail/create/update/delete
```
Include the app URLs in your project `urls.py`:
```python
path("books/", include("myapp.urls")),
```

## 4. Run the server
Apply migrations and browse to `/books/`:
```bash
python manage.py migrate
python manage.py runserver
```
You should see a paginated table with create/update/delete actions using the UI kit configured via `STRAWBERRY_UI`.
