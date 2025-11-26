# Tables

Strawberry ships a `BaseTable` that wraps django-tables2 with sensible defaults and hooks for CRUD actions and selection.

## Default columns
- `selected`: Checkbox column used for bulk actions. Hidden automatically when multi-select/delete is off.
- `actions`: Template column that renders per-row links (view/edit/delete by default).

## Template lookup
Tables resolve templates in this order:
```
{app_label}/tables2.html
strawberry/{UI}/tables2.html
strawberry/default/tables2.html
```
Action partials resolve to:
```
{app_label}/partial/{model_name}_actions.html
strawberry/{UI}/partial/object_actions.html
strawberry/default/partial/object_actions.html
```
Drop a file in your app’s template folder to override either.

## Creating custom tables
```python
from strawberry.tables import BaseTable
from .models import Book

class BookTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Book
        fields = ("title", "author")
```
Pass `table_class = BookTable` on your view, or omit it and let Strawberry auto-generate an equivalent class.

## Pagination and ordering
`BaseCrudView.list()` hands sorting/pagination to django-tables2 via `RequestConfig`. Users can change the page size with a `?page_size=` query parameter.
