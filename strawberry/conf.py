# strawberry/conf.py
from django.conf import settings

UI = getattr(settings, "STRAWBERRY_UI", "default")


FLOWBITE_CHECKBOX_CLASSES = "w-4 h-4 border-gray-300 text-primary-600 focus:ring-primary-500 rounded"
FLOWBITE_TH_CLASSES = "px-4 py-3 font-semibold text-sm border-b border-gray-200"
FLOWBITE_ACTION_CLASSES = "text-right px-4 py-3 font-semibold text-sm border-b border-gray-200"


DEFAULT_CHECKBOX_CLASSES = "checkbox checkbox-primary"
DEFAULT_TH_CLASSES = ""
DEFAULT_ACTION_CLASSES = "text-right"


DAISYUI_CHECKBOX_CLASSES = "checkbox checkbox-primary"
DAISYUI_TH_CLASSES = "px-4 py-3 font-semibold text-sm border-b border-gray-200"
DAISYUI_ACTION_CLASSES = "text-right pe-4"





UI_CHECKBOX_CLASSES = {
    "default": DEFAULT_CHECKBOX_CLASSES,
    "daisyui": DAISYUI_CHECKBOX_CLASSES,
    "flowbite": FLOWBITE_CHECKBOX_CLASSES,
}

UI_TH_CLASSES = {
    "default": DEFAULT_TH_CLASSES,
    "daisyui": DAISYUI_TH_CLASSES,
    "flowbite": FLOWBITE_TH_CLASSES,
}

UI_ACTION_CLASSES = {
    "default": DEFAULT_ACTION_CLASSES,
    "daisyui": DAISYUI_ACTION_CLASSES,
    "flowbite": FLOWBITE_ACTION_CLASSES,
}

ui = UI.lower()
checkbox_classes = UI_CHECKBOX_CLASSES.get(ui, "")
action_classes = UI_ACTION_CLASSES.get(ui, "")
th_classes = UI_TH_CLASSES.get(ui, "")