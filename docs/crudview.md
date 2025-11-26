# CRUD Views

`BaseCrudView` glues Neapolitan’s role-based CRUD views with django-tables2, django-filter, and Strawberry’s UI mixins. Use it directly for general models, or extend `UserBaseCrudView` to scope data to the logged-in user.

## Core attributes
- `model` (required): Django model to manage.
- `fields`: Fields to expose across list/detail/form. Use `"__all__"` for everything.
- `list_fields`, `detail_fields`, `form_fields`: Optional overrides per role.
- `table_class`: Custom django-tables2 class; if omitted, Strawberry auto-generates one inheriting `BaseTable`.
- `allow_delete`, `allow_delete_multiple`, `allow_delete_all`: Turn on per-row delete, bulk delete, and “delete all” actions.
- `allow_multiselect`: Enable a multi-select form hook (see Advanced).
- `paginate_by`: Page size (defaults to `20`; django-tables2 respects the `page_size` query param).

## Filters
Filtering is powered by django-filter:
- Set `allow_filter = False` to disable filtering.
- Use `filter_fields` to whitelist fields for the auto-generated `FilterSet`.
- Provide a custom `filterset_class` for complex filters.
Filter forms inherit the selected UI mixin (Flowbite/DaisyUI/Default) automatically.

## Forms
`BaseCrudView.get_form_class()` builds a ModelForm on the fly and mixes in the UI-specific form mixin so widgets receive the correct CSS classes. Override `get_form_class()` or supply your own form if needed.

## Template resolution
Templates fall back to:
```
{app_label}/{model_name}{suffix}.html
strawberry/{UI}/object{suffix}.html
strawberry/default/object{suffix}.html
```
Partial templates can be overridden per app (see Advanced).

## URL generation
`BaseCrudView.get_urls()` returns a `urlpatterns` list with list, detail, create, update, delete, bulk delete, and multi-select endpoints. Attach it directly in your app’s `urls.py`.

## User-aware CRUD
`UserBaseCrudView` adds:
- Automatic exclusion of the `user` field from forms while injecting `request.user` for validation.
- Querysets filtered to the current user.
- Safe “delete all” that only touches the user’s objects.

## Access control
Use `StaffRequiredMixin` to gate views to staff users and show a friendly message when access is denied.
