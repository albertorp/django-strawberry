# Advanced Usage

## UI selection and styling
Set `STRAWBERRY_UI` to `"flowbite"`, `"daisyui"`, or `"default"` to switch templates and form styling. Both generated ModelForms and filter forms inherit the right mixins so widgets get the correct CSS classes.

## Overriding partials
Strawberry exposes named partials so you can override only slices of the UI. Drop files into your app’s templates to replace them:
- `partial/{model}_{role}_top_title.html`
- `partial/{model}_{role}_top_actions.html`
- `partial/{model}_{role}_filter.html`
- `partial/{model}_{role}_delete_all_modal.html`
- `partial/{model}_{role}_change_multiple_modal.html`
- `partial/{model}_{role}_delete_multiple_modal.html`
- `partial/{model}_{role}_delete_modal.html`

Role is typically `list` or `delete`. If a model-specific template is missing, Strawberry falls back to the bundled `strawberry/{UI}/partial/...` files, then `strawberry/default`.

## Bulk operations
Enable multi-select or bulk deletes:
```python
class OrderView(BaseCrudView):
    # ...
    allow_multiselect = True
    allow_delete_multiple = True
    allow_delete_all = True
    form_multiselect_class = MyBulkEditForm  # required when allow_multiselect=True

    @staticmethod
    def change_multiple_objects(request, selected_objects):
        # custom bulk action
        for obj in selected_objects:
            obj.status = "archived"
            obj.save()
        return True, "Orders archived"
```
`delete_multiple_objects()` already handles `ProtectedError`/`RestrictedError` gracefully.

## Custom filters
Provide a bespoke FilterSet when you need complex lookups:
```python
import django_filters

class BookFilter(django_filters.FilterSet):
    published_after = django_filters.DateFilter(field_name="published_at", lookup_expr="gte")

    class Meta:
        model = Book
        fields = ["author", "published_after"]

class BookView(BaseCrudView):
    model = Book
    filterset_class = BookFilter
```
Otherwise, Strawberry will auto-build a filter set using `filter_fields` or all concrete model fields.

## User-scoped CRUD
Use `UserBaseCrudView` when your model has a `user` field:
- Forms hide the `user` field and inject `request.user`.
- Querysets are limited to the current user.
- “Delete all” acts only on that user’s records.
