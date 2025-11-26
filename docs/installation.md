# Installation

This package bundles Neapolitan, django-tables2, and django-filter to give you a turn-key CRUD stack.

## Requirements
- Python 3.10+
- Django 5.0+ (tested with 5.2)
- A template backend configured with `APP_DIRS=True` and `django.template.context_processors.request`.

## Install the package
```bash
pip install django-strawberry
```

## Django settings
Add the required apps:
```python
INSTALLED_APPS = [
    # ...
    "neapolitan",
    "django_tables2",
    "django_filters",
    "strawberry",
]
```

Pick the UI kit used for generated templates and forms (defaults to `"default"`):
```python
STRAWBERRY_UI = "flowbite"  # or "daisyui" or "default"
```

Ensure your templates can find Strawberry’s bundled templates. With `APP_DIRS=True`, nothing else is needed:
```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # ...
                "django.template.context_processors.request",
            ],
        },
    },
]
```

## Build the docs locally (optional)
From the `docs/` directory:
```bash
make html
```
The rendered site will be in `docs/_build/html/index.html`.
