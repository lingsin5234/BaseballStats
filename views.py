from django.shortcuts import render
from django.forms.models import model_to_dict
import json
from flask import jsonify
from django.core.serializers.json import DjangoJSONEncoder
from .models import StatCollect, JobRequirements
from .oper import db_setup as dbs
from .oper import import_retrosheet as ir
from .oper import process_imports as pi
from .oper import generate_statistics as gs
from .oper import check_latest_imports as chk
from .oper import database_reader as dr
from .oper import class_structure as cs
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
# from .apps import baseball
from .forms import GetYear, ProcessTeam, GenerateStats, ViewStats
from django.contrib import messages
from .functions import instantiate_forms
from djangoapps.utils import get_this_template


# home page
def home_page(request):
    return render(request, 'pages/homepage.html')


# project page
def project_markdown(request):

    page_height = 1050
    f = open('baseball/README.md', 'r')
    if f.mode == 'r':
        readme = f.read()
        page_height = len(readme)/2 + 200

    content = {
        'readme': readme,
        'page_height': page_height
    }

    template_page = get_this_template('baseball', 'project.html')

    return render(request, template_page, content)


# view stats
def stats_view(request):

    # declarations
    results = []
    batting_col = []

    # get batting stats table column names
    cols = cs.batting_stats.columns
    # batting_col = str(cs.batting_stats.columns).replace('batting.', '')
    for i in cols:
        batting_col.append(str(i).replace('batting.', ''))

    # similar to the generate stats form, but gets those that are AVAILABLE.
    year_choices = chk.get_team_choices('view_stats')[1]
    team_choices = chk.get_team_choices('view_stats')[3]
    form_view_stats = ViewStats(year_choices, team_choices, initial={'form_type': 'view_stats'})

    if request.method == 'POST':

        year_choices = chk.get_team_choices('view_stats')[1]
        team_choices = chk.get_team_choices('view_stats')[3]
        form = ViewStats(year_choices, team_choices, request.POST)

        if form.is_valid():
            # read from database
            query = "SELECT * FROM batting WHERE team_name='" + str(request.POST['team']) + "';"
            temp = dr.baseball_db_reader(query)

            # because `temp` is NOT a dictionary we need to convert it!
            results = []
            for t in temp:
                add = dict(zip(batting_col, t))
                # print(add)
                results.append(add)
            # print(results)

        else:
            print(form.errors)

    context = {
        'form_view_stats': form_view_stats,
        'results': json.dumps(results),
        'batting_col': batting_col
    }

    return render(request, 'pages/viewStats.html', context)


# run jobs View
def run_jobs_view(request):

    # DB connect and form initializations
    c = dbs.engine.connect()

    # instantiate all forms
    form_import, form_process, form_gen_stats = instantiate_forms()

    if request.method == 'POST':
        if 'team' in request.POST:
            team = request.POST['team']
        year = request.POST['year']
        if request.POST['form_type'] == 'import_year':

            year_choices = chk.get_year_choices()[1]
            form = GetYear(year_choices, request.POST)

            if form.is_valid():
                status = ir.import_data(request.POST['year'])
                if status:
                    messages.info(request, "Import Completed for " + year)

                    # re-run all the forms!
                    form_import, form_process, form_gen_stats = instantiate_forms()
                else:
                    messages.info(request, year + ' could not be imported')
            else:
                print(form.errors)
        elif request.POST['form_type'] == 'process_team':

            year_choices = chk.get_team_choices('process_team')[1]
            team_choices = chk.get_team_choices('process_team')[3]
            form = ProcessTeam(year_choices, team_choices, request.POST)

            if form.is_valid():
                status = pi.process_data_single_team(year, team)
                if status:
                    messages.info(request, "Processed " + team + " for " + year)

                    # re-run all the forms!
                    form_import, form_process, form_gen_stats = instantiate_forms()
                else:
                    messages.info(request, 'Year has not been Imported.')
            else:
                print(form.errors)
        elif request.POST['form_type'] == 'generate_stats':

            year_choices = chk.get_team_choices('generate_stats')[1]
            team_choices = chk.get_team_choices('generate_stats')[3]
            form = GenerateStats(year_choices, team_choices, request.POST)

            if form.is_valid():
                status = gs.generate_stats(year, team)
                if status:
                    messages.info(request, "Generated Statistics for " + team + " in " + year)

                    # re-run all the forms!
                    form_import, form_process, form_gen_stats = instantiate_forms()
                else:
                    messages.info(request, 'Year has not been Imported OR Team File has not been processed.')
            else:
                print(form.errors)
    else:
        # do nothing as initial forms are already declared
        pass

    query = "SELECT * FROM process_log ORDER BY timestamp DESC LIMIT 10"
    results = [dict(row) for row in c.execute(query).fetchall()]

    # columns wanted
    columns = [{'col': 'process_name'}, {'col': 'data_year'}, {'col': 'team_name'},
               {'col': 'time_elapsed'}, {'col': 'timestamp'}]

    context = {
        'results': json.dumps(results),
        'form_import': form_import,
        'form_process': form_process,
        'form_gen_stats': form_gen_stats,
        'columns': json.dumps(columns)
    }

    return render(request, 'pages/runJobs.html', context)
