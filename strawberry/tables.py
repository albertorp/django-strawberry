from django.template.loader import select_template
from django.utils.safestring import mark_safe

import django_tables2 as tables

class BaseTable(tables.Table):

    selected = tables.CheckBoxColumn(
        accessor='pk',          # ✅ sets value to record.pk automatically
        orderable=False,
        verbose_name='',
    )
    actions = tables.TemplateColumn(
            template_name="strawberry/partial/object_actions.html",
            orderable=False, 
            verbose_name="Actions")

    class Meta:
        abstract = True
        sequence = ('selected', '...', 'actions') # Set in the base class to ensure the actions column is always at the end
        template_name = "strawberry/tables2.html"
        # template_name = "strawberry/tables2_daisyui.html"
        # template_name = "strawberry/tables2_flowbite.html"

    def __init__(self, *args, view=None, **kwargs):
            
        super().__init__(*args, **kwargs)
        self.view = view
                
        if view:
            # We save the query_params to be able to use them later to redirect the user to the same page with the same parameters
            query_params = view.request.GET.copy()
            updated_query_string = query_params.urlencode()
            self.query_string = updated_query_string

            # We also set the multiselect form is needed
            self.change_multiple_form = view.get_change_multiple_form() if view.allow_multiselect else None
        else:
            self.change_multiple_form = None

            


        model = getattr(self.Meta, "model", None)
        if not model:
            return

        app_label = model._meta.app_label
        model_name = model._meta.model_name

        # Candidate list
        template_candidates = [
            f"{app_label}/partial/{model_name}_actions.html",
            "strawberry/partial/object_actions.html",
        ]

        # ✅ Pick the first existing template as a string
        resolved_template = select_template(template_candidates).template.name
        self.base_columns["actions"].template_name = resolved_template

    

    def render_selected(self, value, record):
        return mark_safe(f'<input type="checkbox" name="selected_objects" id="select-{record.pk}" value="{record.pk}">')