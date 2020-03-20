from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import InlineRadios
import os
import numpy as np
from .models import JobRequirements
from .oper import check_latest_imports as chk


class GetYear(forms.ModelForm):

    year = chk.get_year_choices()[0]

    def __init__(self, year_choices, *args, **kwargs):
        super(GetYear, self).__init__(*args, **kwargs)
        self.fields['year'].choices = year_choices

    class Meta:
        model = JobRequirements
        fields = ['year', 'form_type']
        widgets = {'form_type': forms.HiddenInput()}


class ProcessTeam(forms.ModelForm):

    year = chk.get_team_choices('process_team')[0]
    team = chk.get_team_choices('process_team')[2]

    def __init__(self, year_choices, team_choices, *args, **kwargs):
        super(ProcessTeam, self).__init__(*args, **kwargs)
        self.fields['year'].choices = year_choices
        self.fields['team'].choices = team_choices

    class Meta:
        model = JobRequirements
        fields = ['year', 'team', 'form_type']
        widgets = {'form_type': forms.HiddenInput()}


class GenerateStats(forms.ModelForm):

    year = chk.get_team_choices('generate_stats')[0]
    team = chk.get_team_choices('generate_stats')[2]

    def __init__(self, year_choices, team_choices, *args, **kwargs):
        super(GenerateStats, self).__init__(*args, **kwargs)
        self.fields['year'].choices = year_choices
        self.fields['team'].choices = team_choices

    class Meta:
        model = JobRequirements
        fields = ['year', 'team', 'form_type']
        widgets = {'form_type': forms.HiddenInput()}


class ViewStats(forms.ModelForm):

    year = chk.get_team_choices('view_stats')[0]
    team = chk.get_team_choices('view_stats')[2]

    def __init__(self, year_choices, team_choices, *args, **kwargs):
        super(ViewStats, self).__init__(*args, **kwargs)
        self.fields['year'].choices = year_choices
        self.fields['team'].choices = team_choices

    class Meta:
        model = JobRequirements
        fields = ['year', 'team', 'form_type']
        widgets = {'form_type': forms.HiddenInput()}
