# strawberry/conf.py
from django.conf import settings

UI = getattr(settings, "STRAWBERRY_UI", "default")


FLOWBITE_CHECKBOX_CLASSES = (
    "w-4 h-4 border-gray-300 text-primary-600 "
    "focus:ring-primary-500 rounded"
)

DEFAULT_CHECKBOX_CLASSES = (
    "checkbox checkbox-primary"
)

DAISYUI_CHECKBOX_CLASSES = (
    "checkbox checkbox-primary"
)

UI_CHECKBOX_CLASSES = {
    "default": DEFAULT_CHECKBOX_CLASSES,
    "daisyui": DAISYUI_CHECKBOX_CLASSES,
    "flowbite": FLOWBITE_CHECKBOX_CLASSES,
}

ui = UI.lower()
checkbox_classes = UI_CHECKBOX_CLASSES.get(ui, "")