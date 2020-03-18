from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import InlineRadios
from .models import JobRequirements
from .oper import check_latest_imports as chk


class GetYear(forms.ModelForm):

    missing_years = chk.check_years()
    missing_years.reverse()
    year_choices = [(m, m) for m in missing_years]
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
