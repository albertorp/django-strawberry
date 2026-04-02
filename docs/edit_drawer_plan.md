# Plan: HTMX + Alpine.js Edit Drawer (Flowbite)

## Context

Currently, the edit button in the list table navigates to a full-page update form. The goal is an opt-in mode (`allow_edit_drawer = True`) where clicking edit instead opens a right-side drawer and loads the form via HTMX — no page navigation. On save success, the drawer closes and the table refreshes in place. On validation failure, errors appear inside the drawer.

Scope: Flowbite UI theme only (`strawberry/flowbite/` templates + `base_strawberry.html`).

**Prerequisite for users:** HTMX must be included in the project's own base template. Alpine.js is already bundled in `base_strawberry.html`.

---

## Data / Signal Flow

```
User clicks Edit button (row) →
  Alpine: drawerOpen = true              [drawer slides in from right]
  HTMX hx-get → /{url_base}/{pk}/update-drawer/
    └── BaseCrudView.update_drawer() renders object_form_drawer.html
    └── HTMX swaps response into #edit-drawer-body

User submits the form →
  HTMX hx-post → /{url_base}/{pk}/update-drawer/
  ├── INVALID: 200 + form HTML with field errors
  │     └── HTMX swaps into #edit-drawer-body (drawer stays open, errors shown)
  └── VALID: HTTP 204 + response header HX-Trigger: drawerSaveSuccess
        └── Alpine @drawer-save-success.window:
              closeDrawer()                          [drawer slides out]
              htmx.trigger('#object-table-container', 'refreshTable')
                └── HTMX hx-get fires on the table wrapper
                      hx-select extracts only #object-table-container
                      └── Table re-renders in place (preserving filters/sort/pagination)
```

---

## Implementation Steps

### 1. `strawberry/views.py`

#### a) New class attribute

Add alongside other `allow_*` booleans (~line 37):

```python
# When True, the edit button opens a right-side drawer via HTMX
# instead of navigating to a separate update page. Requires HTMX in the project.
allow_edit_drawer = False
```

#### b) New `update_drawer` classmethod

Add alongside `delete_all_records` and `multiple_select` (both are classmethods registered directly in `get_urls`). Add required imports at the top: `from django.http import HttpResponse` and `from django.template.response import TemplateResponse`.

```python
@classmethod
def update_drawer(cls, request, pk):
    """
    HTMX endpoint for the edit drawer.

    GET  — Build the form for the given object and render it as a
           fragment (no base template). HTMX loads this into the drawer body.
    POST — Validate and save the form.
           Success: return HTTP 204 + HX-Trigger header to close the drawer
                    and tell the table to refresh.
           Failure: re-render the form fragment with validation errors so
                    HTMX can swap it back into the drawer body.
    """
    from django.http import HttpResponse
    from django.template.response import TemplateResponse

    # Guard: respect the allow_edit flag on the view class
    if not cls.allow_edit:
        raise PermissionDenied("Editing is not allowed.")

    # Build a temporary view instance so we can call instance methods
    # (get_object, get_form, get_context_data) that expect self.
    instance = cls()
    instance.setup(request)

    # Set kwargs so get_object() can resolve the pk from the URL
    lookup_kwarg = instance.lookup_url_kwarg or instance.lookup_field
    instance.kwargs = {lookup_kwarg: pk}

    # Role.UPDATE ensures get_form_class() and get_context_data()
    # behave as they would on a normal update view.
    instance.role = Role.UPDATE
    instance.template_name_suffix = "_form"

    # Use form_fields if defined, otherwise fall back to the general fields list
    instance.fields = cls.form_fields if cls.form_fields else cls.fields

    # Fetch the object; UserBaseCrudView.get_queryset() will scope this to
    # the current user automatically, so unauthorised access returns 404.
    instance.object = instance.get_object()

    # Resolve the form-fragment template via the existing partial system.
    # Apps can override with e.g. myapp/partial/mymodel_form_drawer.html
    template_name = instance.get_template_partial("form", "drawer")

    if request.method == "GET":
        # Build a bound-to-instance form; UserBaseCrudView.get_form() will
        # inject the user field and remove it from the rendered form.
        form = instance.get_form()
        context = instance.get_context_data(form=form, object=instance.object)
        return TemplateResponse(request, template_name, context)

    # POST: process form submission
    form = instance.get_form()  # get_form_kwargs() picks up request.POST/FILES
    if form.is_valid():
        instance.object = form.save()
        messages.success(
            request,
            _(f"{cls.model.__name__} record successfully updated: {instance.object}")
        )
        # 204 means "no content to swap" — HTMX will not touch the DOM.
        # HX-Trigger fires a browser custom event that Alpine.js listens for
        # to close the drawer and refresh the table.
        response = HttpResponse(status=204)
        response["HX-Trigger"] = "drawerSaveSuccess"
        return response
    else:
        # Return the form fragment with errors; HTMX swaps it into the drawer body.
        context = instance.get_context_data(form=form, object=instance.object)
        return TemplateResponse(request, template_name, context)
```

#### c) Extend `get_urls()`

Add one line after the existing custom URL appends (~line 424):

```python
# Drawer edit endpoint — only reachable when allow_edit_drawer = True on the view
result.append(
    path(
        f'{cls.url_base}/<int:pk>/update-drawer/',
        cls.update_drawer,
        name=f'{cls.url_base}-update-drawer',
    )
)
```

#### d) Extend `get_context_data()`

Add before `return context` (~line 382):

```python
# Pass drawer flag to templates so they can show/hide the right edit button
context['allow_edit_drawer'] = self.allow_edit_drawer

if self.allow_edit_drawer:
    # Resolve the drawer shell template (supports app-level overrides)
    context['template_edit_drawer'] = self.get_template_partial("edit", "drawer")
```

---

### 2. `strawberry/templates/strawberry/base_strawberry.html`

Add a comment in the `<head>` block to instruct users that HTMX must be included if they use the drawer feature. **Do not add an HTMX CDN link** — the project is expected to include HTMX in its own base template.

Add after the Alpine.js `<script>` tag (~line 89):

```html
<!--
  STRAWBERRY: If you use allow_edit_drawer = True on any view, HTMX must be loaded
  before this template renders. Add it to your project's own base template, e.g.:
  <script src="https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js"></script>

  Also add a CSRF header listener so HTMX POST requests pass Django's CSRF check:
  <script>
    document.body.addEventListener('htmx:configRequest', function(evt) {
      evt.detail.headers['X-CSRFToken'] =
        document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? '';
    });
  </script>
-->
```

---

### 3. `strawberry/templates/strawberry/flowbite/object_list.html`

Three changes:

**a) Expand the top-level `<div>` from bare to Alpine-managed:**

Replace:
```html
<div>
```
With:
```html
<!--
  Alpine x-data holds state shared by the delete modal (recordId/recordName)
  and the edit drawer (drawerOpen). The event listener on @drawer-save-success
  reacts to the HX-Trigger header sent by update_drawer() on a successful save.
-->
<div x-data="{
    recordId: null,
    recordName: '',
    drawerOpen: false,
    openEditDrawer() { this.drawerOpen = true; },
    closeDrawer() { this.drawerOpen = false; }
}"
@drawer-save-success.window="
    closeDrawer();
    htmx.trigger('#object-table-container', 'refreshTable')
">
```

**b) Wrap the table in an HTMX-refreshable container:**

Replace:
```html
<div class="my-8">
  {% render_table table %}
</div>
```
With:
```html
<!--
  hx-get refetches this same page URL (preserving current filters/sort/page).
  hx-select extracts only this element from the full response, so the
  rest of the page is untouched. The 'refreshTable' trigger is fired
  programmatically by Alpine after a successful drawer save.
-->
<div id="object-table-container" class="my-8"
     hx-get="{{ request.get_full_path }}"
     hx-trigger="refreshTable"
     hx-target="#object-table-container"
     hx-swap="outerHTML"
     hx-select="#object-table-container">
  {% render_table table %}
</div>
```

**c) Include the drawer shell** just before the closing `</div>` of the Alpine scope:

```html
{% if allow_edit_drawer %}
  {% include template_edit_drawer %}
{% endif %}
```

---

### 4. `strawberry/templates/strawberry/flowbite/partial/object_actions.html`

Replace the single edit `<a>` link with a conditional. When `allow_edit_drawer` is True, render an HTMX button; otherwise keep the original link unchanged.

```html
<!-- Edit -->
{% if allow_edit %}
  {% if allow_edit_drawer %}
  <!--
    Two things happen when this button is clicked:
    1. Alpine @click sets drawerOpen = true, which slides the drawer in.
    2. HTMX hx-get fires to load the form fragment into #edit-drawer-body.
    The URL is built from list_view_url (already in context) + pk + /update-drawer/.
  -->
  <button type="button"
          class="text-gray-600 hover:text-yellow-600 transition cursor-pointer"
          hx-get="{{ list_view_url }}{{ record.pk }}/update-drawer/"
          hx-target="#edit-drawer-body"
          hx-swap="innerHTML"
          @click="openEditDrawer()">
    <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true"
         xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.2"
            d="m14.304 4.844 2.852 2.852M7 7H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-4.5m2.409-9.91a2.017 2.017 0 0 1 0 2.853l-6.844 6.844L8 14l.713-3.565 6.844-6.844a2.015 2.015 0 0 1 2.852 0Z"/>
    </svg>
  </button>
  {% else %}
  <!-- Standard full-page navigation (default behaviour) -->
  <a href="{% url view.url_base|add:'-update' record.pk %}?next={{ request.get_full_path|urlencode }}"
     class="text-gray-600 hover:text-yellow-600 transition">
    <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true"
         xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.2"
            d="m14.304 4.844 2.852 2.852M7 7H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-4.5m2.409-9.91a2.017 2.017 0 0 1 0 2.853l-6.844 6.844L8 14l.713-3.565 6.844-6.844a2.015 2.015 0 0 1 2.852 0Z"/>
    </svg>
  </a>
  {% endif %}
{% endif %}
```

---

### 5. New: `flowbite/partial/object_edit_drawer.html`

The drawer shell. Placed permanently in the DOM (inside the Alpine scope) when `allow_edit_drawer` is True. Alpine drives open/close via `x-show` and CSS transitions.

```html
{% load i18n %}

<!--
  Edit drawer shell — always in the DOM, shown/hidden by Alpine's drawerOpen state.
  The backdrop click calls closeDrawer() to dismiss without saving.
  #edit-drawer-body is the HTMX target where the form fragment is loaded.
-->
<div class="fixed inset-0 z-40 flex justify-end"
     x-show="drawerOpen"
     x-cloak
     x-transition:enter="transition ease-out duration-200"
     x-transition:enter-start="opacity-0"
     x-transition:enter-end="opacity-100"
     x-transition:leave="transition ease-in duration-150"
     x-transition:leave-start="opacity-100"
     x-transition:leave-end="opacity-0">

  <!-- Semi-transparent backdrop; click outside to close -->
  <div class="fixed inset-0 bg-gray-900/50"
       @click="closeDrawer()"></div>

  <!-- Drawer panel — slides in from the right -->
  <div class="relative z-50 w-full max-w-md bg-white shadow-xl flex flex-col h-full"
       x-transition:enter="transition ease-out duration-200 transform"
       x-transition:enter-start="translate-x-full"
       x-transition:enter-end="translate-x-0"
       x-transition:leave="transition ease-in duration-150 transform"
       x-transition:leave-start="translate-x-0"
       x-transition:leave-end="translate-x-full">

    <!-- Drawer header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-200">
      <h3 class="text-base font-semibold text-gray-900">{% trans "Edit" %}</h3>
      <!-- Close button; calls the same Alpine method as the backdrop click -->
      <button type="button"
              class="text-gray-400 hover:bg-gray-200 hover:text-gray-900 rounded-lg p-1.5 text-sm"
              @click="closeDrawer()">
        ✕
      </button>
    </div>

    <!-- Drawer body — HTMX loads the form fragment here on edit button click -->
    <div id="edit-drawer-body"
         class="flex-1 overflow-y-auto p-4">
      <!-- Empty until HTMX populates it -->
    </div>

  </div>
</div>
```

---

### 6. New: `flowbite/partial/object_form_drawer.html`

Pure form fragment — no `{% extends %}`, no base template. Rendered by both the GET and the failed-POST paths of `update_drawer`. HTMX swaps it into `#edit-drawer-body`.

```html
{% load i18n %}

<!--
  Edit form fragment — rendered inside the drawer body, not as a full page.
  hx-post targets the same update-drawer endpoint so HTMX can swap in
  validation errors without closing the drawer or doing a full page reload.
-->
<form method="POST"
      {% if form.is_multipart %}enctype="multipart/form-data"{% endif %}
      hx-post="{{ list_view_url }}{{ object.pk }}/update-drawer/"
      hx-target="#edit-drawer-body"
      hx-swap="innerHTML">

  {% csrf_token %}

  <!-- Non-field errors (e.g. unique_together violations) -->
  {% if form.non_field_errors %}
  <div class="flex p-4 mb-4 text-sm text-error-800 border border-error-300 rounded-lg bg-error-50"
       role="alert">
    <svg class="flex-shrink-0 w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
      <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm1 14a1 1 0 1 1-2 0 1 1 0 0 1 2 0Zm-1-3a1 1 0 0 1-1-1V6a1 1 0 0 1 2 0v4a1 1 0 0 1-1 1Z"/>
    </svg>
    <div>
      {% for error in form.non_field_errors %}
        <div>{{ error }}</div>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  <!-- Form fields — single-column layout (drawer is narrower than full page) -->
  <div class="grid grid-cols-1 gap-4 mb-6">
    {% for field in form %}
    <div class="w-full">
      <!-- Label with required indicator -->
      <label class="block mb-2 text-sm font-medium text-gray-700">
        {{ field.label }}
        {% if field.field.required %}
          <span class="text-error-600">*</span>
        {% endif %}
      </label>

      <!-- Field input (CSS classes applied by FlowbiteFormMixin) -->
      {{ field }}

      <!-- Help text -->
      {% if field.help_text %}
        <p class="mt-1 text-xs text-gray-500">{{ field.help_text }}</p>
      {% endif %}

      <!-- Inline field errors -->
      {% if field.errors %}
        <p class="mt-1 text-xs text-error-600">{{ field.errors|join:", " }}</p>
      {% endif %}
    </div>
    {% endfor %}
  </div>

  <!-- Action buttons -->
  <div class="flex items-center gap-3 pt-2">
    <button type="submit"
            class="text-white bg-primary-600 hover:bg-primary-700 focus:ring-4 focus:ring-primary-300
                   font-medium rounded-lg text-sm px-5 py-2.5">
      {% trans "Save" %}
    </button>
    <!--
      Cancel calls closeDrawer() on the parent Alpine scope — no page navigation,
      just hides the drawer. Any unsaved changes are discarded.
    -->
    <button type="button"
            class="text-gray-700 bg-gray-100 hover:bg-gray-200 focus:ring-4 focus:ring-gray-300
                   font-medium rounded-lg text-sm px-5 py-2.5"
            @click="closeDrawer()">
      {% trans "Cancel" %}
    </button>
  </div>
</form>
```

---

## Files to Modify

- [strawberry/views.py](strawberry/views.py)
- [strawberry/templates/strawberry/base_strawberry.html](strawberry/templates/strawberry/base_strawberry.html)
- [strawberry/templates/strawberry/flowbite/object_list.html](strawberry/templates/strawberry/flowbite/object_list.html)
- [strawberry/templates/strawberry/flowbite/partial/object_actions.html](strawberry/templates/strawberry/flowbite/partial/object_actions.html)

## Files to Create

- `strawberry/templates/strawberry/flowbite/partial/object_edit_drawer.html`
- `strawberry/templates/strawberry/flowbite/partial/object_form_drawer.html`

---

## Notes

- **`UserBaseCrudView` compatibility**: `instance.get_form()` resolves through MRO, so `UserBaseCrudView.get_form()` (injects `user`, hides the user field) applies automatically — no special handling needed.
- **Permission scoping**: `instance.get_object()` uses `get_queryset()`, which in `UserBaseCrudView` filters by `user=request.user`. A user cannot load another user's record; they get a 404.
- **Template overrides**: `get_template_partial("form", "drawer")` follows the existing resolution order, so apps can override with `{app_label}/partial/{model_name}_form_drawer.html`.
- **`allow_edit = False`**: The edit button is already hidden by `{% if allow_edit %}` in `object_actions.html`. The view method also guards with `raise PermissionDenied` for belt-and-suspenders.
- **HTMX not bundled**: HTMX must be added to the project's own base template. A comment in `base_strawberry.html` tells users what to add and where.
- **DaisyUI**: Out of scope for this change.

## Verification

1. Set `allow_edit_drawer = True` on a view in the example project (e.g. `SampleModelView`)
2. `python manage.py runserver`, navigate to the list view
3. Click the pencil icon — verify the drawer slides in from the right and the form loads
4. Submit with invalid data — verify errors appear inside the drawer, no page reload
5. Submit with valid data — verify the drawer closes, the table row updates in place
6. Test with `SampleModelView` (which uses `UserBaseCrudView`) — verify user field is hidden and injected correctly
7. Test `allow_edit_drawer = False` (default) — verify the original link navigation is unchanged
