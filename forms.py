from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import InlineRadios
import os
import numpy as np
from .models import JobRequirements
from .oper import check_latest_imports as chk


class GetYear(forms.ModelForm):

    missing_years = chk.check_years()
    if missing_years is None:
        year = forms.ChoiceField(required=True, label='Year', choices=('', '----'))
    else:
        missing_years.reverse()
        year_choices = [(m, m) for m in missing_years]
        year = forms.ChoiceField(required=True, label='Year', choices=year_choices)

    class Meta:
        model = JobRequirements
        fields = ['year', 'form_type']
        widgets = {'form_type': forms.HiddenInput()}


class ProcessTeam(forms.ModelForm):

    # get years that have already been imported
    all_dir = os.listdir('baseball/import')
    imported_years = [y for y in all_dir if y.isnumeric()]

    # check if anything there
    if imported_years is None:
        year = forms.ChoiceField(required=True, label='Year', choices=('', '----'))
    else:
        imported_years.reverse()
        year_choices = [(i, i) for i in imported_years]
        year = forms.ChoiceField(required=True, label='Year', choices=year_choices)

        # check for teams for all years selected
        processed_teams = []
        for y in imported_years:
            p_teams = chk.check_teams(y, 'process_team')
            processed_teams.extend(p_teams)
            # print(processed_teams)

        processed_teams = sorted(np.unique(processed_teams))
        team_choices = [(t, t) for t in processed_teams]
        team = forms.ChoiceField(required=True, label='Team', choices=team_choices)
        # print(team_choices)

    class Meta:
        model = JobRequirements
        fields = ['year', 'team', 'form_type']
        widgets = {'form_type': forms.HiddenInput()}


class GenerateStats(forms.ModelForm):

    # get years that have already been imported
    all_dir = os.listdir('baseball/import')
    imported_years = [y for y in all_dir if y.isnumeric()]

    # check if anything there
    if imported_years is None:
        year = forms.ChoiceField(required=True, label='Year', choices=('', '----'))
    else:
        imported_years.reverse()
        year_choices = [(i, i) for i in imported_years]
        year = forms.ChoiceField(required=True, label='Year', choices=year_choices)

        # check for teams for all years selected
        processed_teams = []
        for y in imported_years:
            p_teams = chk.check_teams(y, 'gen_stats')
            processed_teams.extend(p_teams)
            # print(processed_teams)

        processed_teams = sorted(np.unique(processed_teams))
        team_choices = [(t, t) for t in processed_teams]
        team = forms.ChoiceField(required=True, label='Team', choices=team_choices)

    def __init__(self, team_choices, *args, **kwargs):
        super(GenerateStats, self).__init__(*args, **kwargs)
        self.fields['team'].choices = team_choices

    class Meta:
        model = JobRequirements
        fields = ['year', 'team', 'form_type']
        widgets = {'form_type': forms.HiddenInput()}
