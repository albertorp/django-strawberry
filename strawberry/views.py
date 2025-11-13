from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError, RestrictedError
from django.shortcuts import redirect
from django.template.loader import select_template
from django.urls import path, reverse
from django.utils.decorators import classonlymethod
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _

from neapolitan.views import CRUDView, Role
from django_tables2.views import SingleTableMixin
from django_tables2 import RequestConfig



class BaseCrudView(SingleTableMixin, CRUDView):
    
    paginate_by = 20

    # Allow the user to delete items in the DB from the listview
    allow_delete = False

    # Allow the user to delete MULTIPLE items in the DB from the listview in one go (CAUTION)
    allow_delete_multiple = False

    # Allow the user to delete ALL items in the DB from the listview in one go (CAUTION)
    allow_delete_all = False

    # Allow the user to select multiple rows
    allow_multiselect = False

    form_multiselect_class = None # Each subview must define the form for multiselect behaviour that they want to implement
    table_class = None  # Each subview must define the table to be used


    def get_template_names(self):
        """
        Returns a list of template names to use when rendering the response.

        This is overriding the method to change the fallback folder from neapolitan/... to strawberry/...

        If `.template_name` is not specified, uses the
        "{app_label}/{model_name}{template_name_suffix}.html" model template
        pattern, with the fallback to the
        "strawberry/object{template_name_suffix}.html" default templates.
        """
        if self.template_name is not None:
            return [self.template_name]

        if self.model is not None and self.template_name_suffix is not None:
            return [
                f"{self.model._meta.app_label}/"
                f"{self.model._meta.object_name.lower()}"
                f"{self.template_name_suffix}.html",
                f"strawberry/object{self.template_name_suffix}.html",
            ]
        msg = (
            "'%s' must either define 'template_name' or 'model' and "
            "'template_name_suffix', or override 'get_template_names()'"
        )
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def get_table_kwargs(self):
        kwargs = super().get_table_kwargs()
        kwargs['view'] = self
        return kwargs


    def get_table_pagination(self, table):
        """
        Wwe need this method to be able to add a dropdown to the navigation block and change the number of items (rows)
        displayed in the table
        """
        page_size = self.request.GET.get("page_size", 10)
        return {"per_page": int(page_size)}
    

    def get_paginate_by(self, table_data=None):
        """
        This is needed here to avoid a conflict between SingleTableMixin and CRUDView. Both have the same method with different
        signatures. Since we want to handle pagination via django-tables2, we just keep this
        """
        return getattr(self, "paginate_by", None)
    

    def get_table_data(self):
        """
        Return the queryset used to populate the table.
        Ensures Neapolitan's filtering is applied.
        """
        queryset = self.get_queryset()
        filterset = self.get_filterset(queryset)
        if filterset is not None:
            queryset = filterset.qs
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Override Neapolitan's list() to delegate sorting/pagination to django-tables2.

        This is because with neapolitan and django-tables2 there were conflicts with the ordering and we were 
        getting exceptions
        """
        table = self.get_table(view=self)

        RequestConfig(
            request,
            paginate=self.get_table_pagination(table)
        ).configure(table)

        # Keep consistency with Neapolitan templates
        self.object_list = table.data.data

        context = self.get_context_data(
            table=table,
            filterset=self.get_filterset(self.get_queryset()),
            page_obj=getattr(table, "page", None),
            is_paginated=hasattr(table, "page"),
            paginator=getattr(table, "paginator", None),
        )

        context["object_list"] = self.object_list
        context[self.get_context_object_name(is_list=True)] = self.object_list

        return self.render_to_response(context)
    

    def get_template_partial(self, role, partial):
        model = getattr(self, "model", None)
        if not model:
            return

        app_label = model._meta.app_label
        model_name = model._meta.model_name

        # Candidate list
        template_candidates = [
            f"{app_label}/partial/{model_name}_{role}_{partial}.html",
            f"neapolitan/partial/object_{role}_{partial}.html",
        ]

        # ✅ Pick the first existing template as a string
        resolved_template = select_template(template_candidates).template.name

        return resolved_template



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['allow_delete'] = self.allow_delete
        context['allow_delete_all'] = self.allow_delete_all
        context['allow_delete_multiple'] = self.allow_delete_multiple
        context['allow_multiselect'] = self.allow_multiselect
        # context['allow_duplicate'] = self.allow_duplicate

        context["list_view_url"] = Role.LIST.maybe_reverse(self)

        # templates
        context['template_top_title'] = self.get_template_partial("list", "top_title")
        context['template_top_actions'] = self.get_template_partial("list", "top_actions")
        context['template_list_filter'] = self.get_template_partial("list", "filter" )
        context['template_delete_modal'] = self.get_template_partial("delete", "modal")


        if self.allow_delete_all:
            context["delete_all_url"] = Role.LIST.maybe_reverse(self)+'delete-all/'



        if self.role == Role.LIST:
            filterset_class = getattr(self, "filterset_class", None)
            if filterset_class is not None:
                filterset = self.get_filterset()
                context['form_filter'] = filterset.form 

            # TODO This was copied over from previouse versions and used in the multiselect, but perhaps it's not needed
            # Earlier we had to remove some query string parameters, but now that the sorting is handled by django-tables2
            # we may be able to skip it
            query_params = self.request.GET.copy()
            updated_query_string = query_params.urlencode()
            context['query_string'] = updated_query_string

        if self.allow_multiselect or self.allow_delete_multiple:
            self.multiselect_url = Role.LIST.maybe_reverse(self)+'multiple-select/'
            context["multiselect_url"] = self.multiselect_url
            # if self.role == Role.LIST:
            #     context['change_multiple_form'] = self.get_change_multiple_form()


        return context
    



    @classmethod
    def delete_all_records(cls, request):
        if request.method == 'POST':
            try:
                if cls.allow_delete_all:
                    # Access the model class
                    model = cls.model

                    # Delete all records in the model
                    model.objects.all().delete()

                    messages.success(request, _("All records have been deleted successfully."))
                else:
                    messages.warning(request, _("Deleting all records is not allowed."))
            except:
                messages.error(request, _("An error occurred while deleting records."))

            # Construct the URL for redirection
            app_name = model._meta.app_label
            url = f'/{app_name}/{cls.url_base}'

            # Redirect to the constructed URL
            return redirect(url)
        else:
            messages.error(request, _("Invalid request method."))
            return redirect('/')
        


    @classonlymethod
    def get_urls(cls, roles=None):
        """
        Classmethod to generate URL patterns for the view.
        This will allow us to add the delete_all and multiple-select paths
        """
        result = super().get_urls(roles)
        result.append(path(f'{cls.url_base}/delete-all/', cls.delete_all_records, name='delete_all_records'))
        result.append(path(f'{cls.url_base}/multiple-select/', cls.multiple_select, name='multiple_select'))
        return result
    

    def process_deletion(self, request, *args, **kwargs):
        obj = self.get_object()
        result = super().process_deletion(request, *args, **kwargs)
        messages.success(request, _(f"{self.model.__name__} record successfully deleted: {obj}"))

        next_url = request.POST.get("next") or request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            # The extra check for has_allowed_host... allows us to prevent open redirects, by validating that next_url is local
            # Override the default redirect target
            result['Location'] = next_url
            
        return result
    

    def get_success_url(self):
        """
        Overriding the neapolitan implementation because I want to return always to the list view, not to the detail view
        """
        assert self.model is not None, (
            "'%s' must define 'model' or override 'get_success_url()'"
            % self.__class__.__name__
        )
        next_url = self.request.POST.get("next")
        if next_url:
            return next_url
        
        success_url = reverse(f"{self.url_base}-list")
        return success_url
    

    def get_change_multiple_form_class(self):
        """
        Returns the form class to use in this view for multiselect forms.
        """
        if self.form_multiselect_class is not None:
            return self.form_multiselect_class
        
        msg = (
            "'%s' must define 'form_multiselect_class' or override 'get_change_multiple_form_class()'"
        )
        raise ImproperlyConfigured(msg % self.__class__.__name__)


    def get_change_multiple_form(self, **kwargs):
        """
        Returns a form instance for multiselect forms.
        """
        cls = self.get_change_multiple_form_class()
        return cls(**kwargs)
    

    def change_multiple_objects(request, selected_objects):
        """
        This method is called when the user selects multiple objects and clicks the "Change" button.
        It should be overridden in the child class to implement the desired functionality.

        Returns:
            result: boolean to indicate success or failure
            msg: message explaining the success or failure
        """
        # This is the default implementation that does nothing.
        # Override this method in the child class to implement the desired functionality.
        for obj in selected_objects:
            print(obj.id, obj)
            pass

        return True, _('Blank implementation')
    

    def delete_multiple_objects(request, selected_objects):
        """
        This method is called when the user selects multiple objects and clicks 
        the "Delete Multiple" button.

        Returns:
            result: boolean to indicate success or failure
            msg: message explaining the success or failure
        """
        errors = []
        deleted_count = 0

        for obj in selected_objects:
            try:
                # Wrap each delete in its own transaction so one failure 
                # doesn’t roll back all the previous deletions
                with transaction.atomic():
                    obj.delete()
                deleted_count += 1

            except ProtectedError as e:
                errors.append(
                    _("Cannot delete %(obj)s because related objects protect it.") 
                    % {"obj": str(obj)}
                )
            except RestrictedError as e:
                errors.append(
                    _("Cannot delete %(obj)s because related objects restrict it.") 
                    % {"obj": str(obj)}
                )
            except IntegrityError as e:
                errors.append(
                    _("Database integrity error while deleting %(obj)s: %(err)s") 
                    % {"obj": str(obj), "err": str(e)}
                )
            except Exception as e:
                errors.append(
                    _("Unexpected error while deleting %(obj)s: %(err)s") 
                    % {"obj": str(obj), "err": str(e)}
                )

        if errors:
            msg = _("Deleted %(count)d objects, but some errors occurred:\n%(errors)s") % {
                "count": deleted_count,
                "errors": "\n".join(errors),
            }
            return False, msg

        return True, _("Successfully deleted %(count)d objects.") % {"count": deleted_count}
    

    @classmethod
    def multiple_select(cls, request):
        if request.method == 'POST':

            if cls.multiple_select:
                # Access the model class
                model = cls.model

            selected_ids = request.POST.getlist('selected_objects')

            if selected_ids:
            # Remove the "select_all" value (it comes as a 0 in the list of selected ids)
                if '0' in selected_ids:
                    selected_ids.remove('0')

                # Get all the selected objects from the DB
                selected_objects = model.objects.filter(id__in=selected_ids)

                if 'delete_multiple' in request.POST:
                    result, msg = cls.delete_multiple_objects(request, selected_objects)
                else:
                    result, msg = cls.change_multiple_objects(request, selected_objects)
                if result:
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
            else:
                messages.warning(request, _('No objects selected'))

            # Construct the URL for redirection
            app_name = model._meta.app_label
            query_string = request.META.get("QUERY_STRING", "") # To preserve query parameters (filters or sorting)
            url = f'/{app_name}/{cls.url_base}/?{query_string}' if query_string else f'/{app_name}/{cls.url_base}/'

            # Redirect to the constructed URL
            return redirect(url)
        else:
            messages.error(request, _("Invalid request method."))
            return redirect('/')
        


    def form_valid(self, form):
        result = super().form_valid(form)
        
        # TODO Translate the messages
        if self.role == Role.CREATE:
            msg = _(f"New {self.model.__name__} record successfully created: {self.object} ")
        
        if self.role == Role.UPDATE:
            msg = _(f"{self.model.__name__} record successfully updated: {self.object} ")

        messages.success(self.request, msg)
        return result