from django.conf import settings
from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title
    


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    iso_code = models.CharField(max_length=3, unique=True)

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    def __str__(self):
        return self.name


class SampleModel(models.Model):
    """
    A model representing a sample for a project.

    This model is just a collection of typical fields that can be used in a project, and it will have an accompanying
    admin panel, form, and templates to demonstrate basic CRUD functionality.

    You can use these or copy and/or delete them as needed in your app

    Fields:
        - date (DateField): The date of the sample.
        - name (CharField): The name of the sample (required).
        - email (EmailField): The email of the sample.
        - phone (CharField): The phone of the sample.
        - description (TextField): The description of the sample.
        - status (IntegerField): The status of the sample.
        - active (BooleanField): The active status of the sample.
        - integer (IntegerField): The integer value of the sample.
        - decimal (DecimalField): The decimal value of the sample.
        - user (ForeignKey): The user associated with the sample (required).
        - country (ForeignKey): The country associated with the sample.

    Methods:
        - get_status_display(): Returns a human-readable version of the sample's status.

    """
    STATUS_CHOICES = (
        (1, _('Draft')),
        (2, _('Started')),
        (3, _('Finished')),
        (4, _('Closed')),
    )

    date = models.DateField(verbose_name=_('Date'), help_text=_('The date of the sample.'))
    name = models.CharField(verbose_name=_('Name'), help_text=_('The name of the sample.'), max_length=30)
    email = models.EmailField(verbose_name=_('Email'), help_text=_('The email of the sample.'), blank=True, null=True)
    phone = models.CharField(verbose_name=_('Phone'), help_text=_('The phone of the sample.'), max_length=20, blank=True, null=True)
    description = models.TextField(verbose_name=_('Description'), help_text=_('The description of the sample.'), blank=True, null=True)
    status = models.IntegerField(verbose_name=_('Status'), help_text=_('The status of the sample.'), choices=STATUS_CHOICES, default=1, blank=True, null=True)
    active = models.BooleanField(verbose_name=_('Active'), help_text=_('The active status of the sample.'), default=False, blank=True, null=True)
    integer = models.IntegerField(verbose_name=_('Integer'), help_text=_('The integer value of the sample.'), blank=True, null=True)
    decimal = models.DecimalField(verbose_name=_('Decimal'), help_text=_('The decimal value of the sample.'), max_digits=10, decimal_places=2, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='samples', verbose_name=_('User'), help_text=_('The user associated with the sample.'))
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='countries', verbose_name=_('Country'), help_text=_('The country associated with the sample.'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Sample')
        verbose_name_plural = _('Samples')

    def __str__(self):
        return self.name
    
    def get_status_display(self):
        """
        Returns a human-readable version of the sample's status.
        """
        return self.STATUS_CHOICES[self.status - 1][1]
    

    """
    This is only to test validation errors
    """
    # def clean(self):
    #     super().clean()
    #     non_field_errors = []

    #     non_field_errors.append("Error A happened.")

    #     non_field_errors.append("Error B happened.")

    #     if non_field_errors:
    #         raise ValidationError({"__all__": non_field_errors})
    
