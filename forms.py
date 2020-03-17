from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import InlineRadios
from .models import JobRequirements


class GetYear(forms.ModelForm):

    year_choices = [(c.year, c.year) for c in JobRequirements.objects.filter(form_type='import_year')]

    year = forms.ChoiceField(required=True, label='Year', choices=year_choices)

    class Meta:
        model = JobRequirements
        fields = ['year', 'form_type']
        widgets = {'form_type': forms.HiddenInput()}


class ProcessTeam(forms.ModelForm):
    class Meta:
        model = JobRequirements
        fields = ['year', 'team', 'form_type']
        widgets = {'form_type': forms.HiddenInput()}


class GenerateStats(forms.ModelForm):
    class Meta:
        model = JobRequirements
        fields = ['year', 'team', 'form_type']
        widgets = {'form_type': forms.HiddenInput()}
