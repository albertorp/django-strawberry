from django.template.loader import select_template
from django.utils.safestring import mark_safe

import django_tables2 as tables

from .conf import UI, checkbox_classes, UI_CHECKBOX_CLASSES, action_classes, th_classes, STRAWBERRY_DATE_FORMAT


class BaseTable(tables.Table):

    selected = tables.CheckBoxColumn(
        accessor='pk',          # ✅ sets value to record.pk automatically
        orderable=False,
        verbose_name='',
        attrs={
            "th": {"class": "w-8 min-w-[3rem] max-w-[3rem] text-center"},
            "td": {"class": "w-8 min-w-[3rem] max-w-[3rem] text-center"},
            "th__input": {"class": checkbox_classes},
        }
    )
    actions = tables.TemplateColumn(
            template_name=f"strawberry/{UI}/partial/object_actions.html", # This will be changed in init
            # template_name = None,
            orderable=False, 
            verbose_name="Actions",
            attrs={
                    "th": {"class": action_classes},
                }
            )
    

    class Meta:
        abstract = True
        row_attrs = {"id": lambda record: "row"+str(record.pk)}
        sequence = ('selected', '...', 'actions') # Set in the base class to ensure the actions column is always at the end
        template = None
        # template_name = f"strawberry/{UI}/tables2.html"
        # template_name = "strawberry/tables2_daisyui.html"
        # template_name = "strawberry/tables2_flowbite.html"

        # Header attributes for *all* columns
        attrs = {
            "th": {
                "class": th_classes,
            },
        }

    default_template_name = f"strawberry/{UI}/tables2.html"

    def __init__(self, *args, view=None, **kwargs):
        for name, col in self.base_columns.items():
            if isinstance(col, tables.DateColumn):
                # col.format = DATE_FORMAT
                col.localize = False
                col.render = lambda value, **_: value.strftime(STRAWBERRY_DATE_FORMAT) if value else ""

        super().__init__(*args, **kwargs)

        self.view = view                
        if view:
            # We save the query_params to be able to use them later to redirect the user to the same page with the same parameters
            query_params = view.request.GET.copy()
            updated_query_string = query_params.urlencode()
            self.query_string = updated_query_string

            # We also set the multiselect form is needed
            self.change_multiple_form = view.get_change_multiple_form() if view.allow_multiselect else None

            # Remove the "selected" column when neither multiselect or delete_multiple are allowed
            if not view.allow_delete_multiple and not view.allow_multiselect:
                # 2025 12 01 This check was giving an error when using a derived BaseTable for a model
                # if "selected" in self.base_columns:
                #     del self.base_columns["selected"]
                if "selected" in self.columns:
                    self.columns.hide("selected")

                    
        else:
            self.change_multiple_form = None

            
        model = getattr(self.Meta, "model", None)
        if not model:
            return

        app_label = model._meta.app_label
        model_name = model._meta.model_name

        # Set the table template
        if not getattr(self.Meta, "template_name", None):
            template_candidates = [
                f"{app_label}/tables2.html",
                f"strawberry/{UI}/tables2.html",
                f"strawberry/default/tables2.html",
                "strawberry/tables2.html",
            ]
            resolved_template = select_template(template_candidates).template.name
            self.template_name = resolved_template


        # Set the object actions template
        # TODO Change this to allow to specify it also via an attribute in the child class
        template_candidates = [
            f"{app_label}/partial/{model_name}_actions.html",
            f"strawberry/{UI}/partial/object_actions.html",
            f"strawberry/default/partial/object_actions.html",
            "strawberry/partial/object_actions.html",
        ]

        # ✅ Pick the first existing template as a string
        resolved_template = select_template(template_candidates).template.name
        self.base_columns["actions"].template_name = resolved_template

        self.template_list_change_multiple_modal = view.template_list_change_multiple_modal
        self.template_list_delete_multiple_modal = view.template_list_delete_multiple_modal

    

    def render_selected(self, value, record):
        ui = UI.lower()
        checkbox_classes = UI_CHECKBOX_CLASSES.get(ui, "")
        return mark_safe(f'<input type="checkbox" name="selected_objects" id="select-{record.pk}" value="{record.pk}" class="{checkbox_classes}">')
    