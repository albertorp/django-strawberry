




from django import forms


class DefaultFormMixin:
    """UI-neutral - applies no classes."""
    pass


class DaisyUIFormMixin:
    input_class = "input input-bordered w-full"
    select_class = "select select-bordered w-full"
    textarea_class = "textarea textarea-bordered w-full"
    checkbox_class = "checkbox checkbox-primary"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            widget = field.widget
            cls = widget.__class__.__name__

            # Text inputs
            if hasattr(widget, "input_type") and widget.input_type != "checkbox":
                widget.attrs.setdefault("class", self.input_class)

            # Checkbox
            elif cls == "CheckboxInput":
                widget.attrs.setdefault("class", self.checkbox_class)

            # Select
            elif cls in ["Select", "SelectMultiple"]:
                widget.attrs.setdefault("class", self.select_class)

            # Textarea
            elif cls == "Textarea":
                widget.attrs.setdefault("class", self.textarea_class)
                


class FlowbiteFormMixin:
    base_input_class = (
        "block w-full border px-2 py-2.5 rounded-lg border-gray-300 text-gray-900 text-sm "
        "focus:ring-primary-500 focus:border-primary-500"
    )

    base_select_class = (
        "block w-full rounded-lg px-2 py-2.5 border border-gray-300 bg-white text-gray-900 text-sm "
        "focus:ring-primary-500 focus:border-primary-500"
    )

    base_checkbox_class = (
        "w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded "
        "focus:ring-primary-500"
    )

    base_textarea_class = (
        "block w-full px-2 py-2.5 rounded-lg border border-gray-300 text-gray-900 text-sm "
        "focus:ring-primary-500 focus:border-primary-500"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            widget = field.widget
            cls = widget.__class__.__name__

            if hasattr(widget, "input_type") and widget.input_type != "checkbox":
                widget.attrs.setdefault("class", self.base_input_class)

            elif cls in ["Select", "SelectMultiple"]:
                widget.attrs.setdefault("class", self.base_select_class)

            elif cls == "Textarea":
                widget.attrs.setdefault("class", self.base_textarea_class)
                widget.attrs["rows"] = 3

            elif cls == "CheckboxInput":
                widget.attrs.setdefault("class", self.base_checkbox_class)

            if isinstance(field, forms.DateField):
                field.widget = forms.TextInput(
                    attrs={
                        "type": "text",
                        "class": (
                            "block w-full px-2 py-2.5 rounded-lg border border-gray-300 bg-white "
                            "text-gray-900 text-sm focus:ring-primary-500 focus:border-primary-500"
                        ),
                        "datepicker": "",
                        "datepicker-autohide": "",
                        "datepicker-format": "yyyy-mm-dd",
                    }
                )
                continue


UI_MIXINS = {
    "default": DefaultFormMixin,
    "daisyui": DaisyUIFormMixin,
    "flowbite": FlowbiteFormMixin,
}


