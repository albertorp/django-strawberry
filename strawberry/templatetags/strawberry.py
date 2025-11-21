from django import template
from django.template.loader import get_template
from django.template import Context

register = template.Library()


# @register.inclusion_tag("strawberry/partial/detail.html")
# def object_detail(object, fields):
#     """
#     Renders a detail view of an object with the given fields.

#     Inclusion tag usage::

#         {% object_detail object fields %}

#     Template: ``strawberry/partial/detail.html`` - Will render a table of the
#     object's fields.
#     """

#     def iter():
#         for f in fields:
#             mf = object._meta.get_field(f)
#             yield (mf.verbose_name, mf.value_to_string(object))

#     return {"object": iter()}


@register.simple_tag(takes_context=True)
def object_detail(context, object, fields):
    from strawberry.conf import UI
    template_name = f"strawberry/{UI}/partial/detail.html"
    t = get_template(template_name)
    iter_fields = [(object._meta.get_field(f).verbose_name,
                    object._meta.get_field(f).value_to_string(object))
                   for f in fields]
    new_context = {
        "object": iter_fields,
    }
    # propagate csrf_token, request, etc as needed
    if "csrf_token" in context:
        new_context["csrf_token"] = context["csrf_token"]
    if "request" in context:
        new_context["request"] = context["request"]
    return t.render(new_context)
