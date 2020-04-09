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
from .oper import global_variables as gv
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
# from .apps import baseball
from .forms import GetYear, ProcessTeam, GenerateStats, ViewStats
from django.contrib import messages
from .functions import instantiate_forms
from djangoapps.utils import get_this_template
from datetime import time


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
    for i in cols:
        batting_col.append(str(i).replace('batting.', ''))
    batting_col = batting_col[1:len(batting_col)]  # ignore ID

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
                t = t[1:len(t)]  # ignore the ID in first column!
                add = dict(zip(batting_col, t))
                # add.pop('Id', None)
                # print(add)
                results.append(add)
            # print(results)

        else:
            print(form.errors)

    context = {
        'form_view_stats': form_view_stats,
        'results': json.dumps(results),
        'batting_col': batting_col,
        'col_convert': json.dumps(gv.bat_stat_types)
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


# this will replace the runJobs with a dashboard of the automated jobs
def jobs_dashboard(request):

    # the main 3 processes
    processes = [{'p': 'import_year'}, {'p': 'play_processor'}, {'p': 'stat_processor'}]

    # get column names of process_log table
    process_col = []
    cols = cs.process_log.columns
    for i in cols:
        process_col.append(str(i).replace('process_log.', ''))

    # years that have been imported
    query = "SELECT * FROM process_log WHERE process_name='import_year'"
    results = dr.baseball_db_reader(query)

    # for each row (tuple), sort and add columns
    years_imported = []
    for r in results:
        years_imported.append(dict(zip(process_col, r)))

    # for each year imported, check number of teams in total
    all_years = chk.get_years()
    all_years.reverse()
    num_teams_array = []
    for y in all_years:
        num_teams = chk.check_teams(y, 'total_num_teams')
        num_teams_array.append({'data_year': y, 'num_teams': num_teams})

    # teams that have been processed -- by year
    query = "SELECT data_year, COUNT(team_name) FROM process_log WHERE process_name='play_processor' "
    query += "GROUP BY data_year ORDER BY data_year desc"
    results = dr.baseball_db_reader(query)

    # for each row (tuple), sort and add columns
    teams_processed = []
    for r in results:
        teams_processed.append(dict(zip(['data_year', 'num_teams'], r)))

    # go thru and divide teams/processed by total num of teams
    for n in num_teams_array:
        year = int(n['data_year'])
        num_teams = n['num_teams']
        for t in teams_processed:
            if t['data_year'] == year:
                t['num_teams'] = t['num_teams'] / num_teams
                # print(t)
                break

    if len(num_teams_array) > len(teams_processed):
        missing_years = len(num_teams_array) - len(teams_processed)
        len_index = len(num_teams_array) - 1
        for m in range(missing_years):
            num_teams_array[len_index]['num_teams'] = 0
            teams_processed.append(num_teams_array[len_index])
            len_index -= 1
    # print(teams_processed)

    # teams that have stats generated -- by year
    query = "SELECT data_year, COUNT(team_name) FROM process_log WHERE process_name='stat_processor' "
    query += "GROUP BY data_year ORDER BY data_year desc"
    results = dr.baseball_db_reader(query)

    # for each row (tuple), sort and add columns
    stats_generated = []
    for r in results:
        stats_generated.append(dict(zip(['data_year', 'num_teams'], r)))

    # go thru and divide teams/processed by total num of teams
    for s in stats_generated:
        year = s['data_year']
        for n in num_teams_array:
            if int(n['data_year']) == year:
                s['num_teams'] = s['num_teams'] / int(n['num_teams'])
                # print(t)
                break

    # 10 most recent processes run
    recent_10 = []
    query = 'SELECT process_name, team_name, time_elapsed, timestamp FROM process_log ORDER BY timestamp desc LIMIT 10'
    results = dr.baseball_db_reader(query)
    # results = dr.baseball_db_reader("SELECT * FROM process_log WHERE process_name='x'")
    for r in results:
        recent_10.append(dict(zip(['Process', 'Team', 'Elapsed', 'Timestamp'], r)))
    min_time = time(0, 0)
    max_time = time(0, 0)
    if len(recent_10) == 0:
        recent_10 = [{'results': 'NO RESULTS!'}]
    elif len(recent_10) < 10:
        min_time = recent_10[len(recent_10)-1]['Timestamp']
        max_time = recent_10[0]['Timestamp']
    else:
        min_time = recent_10[9]['Timestamp']
        max_time = recent_10[0]['Timestamp']
    max_time_elapsed = max([val for val in [item['Elapsed'] for item in recent_10]])
    # print(max_time_elapsed)

    # find the error rate based on gameplay
    query = 'SELECT COUNT(*) FROM processing_errors'
    results = dr.baseball_db_reader(query)
    errors = int(results[0][0])

    query = 'SELECT COUNT(*) FROM gameplay'
    results = dr.baseball_db_reader(query)
    total = int(results[0][0])
    success = total - errors

    error_rate = {'success': round(100 * success / total, 5)}
    error_rate.update({'error': round(100 * errors / total, 5)})
    # print(error_rate)

    # group team: data hits, rbis, home_runs; MUST GROUP BY YEAR LATER!!
    query = 'SELECT SUM(hits), SUM(home_runs), SUM(rbis), team_name FROM batting GROUP BY team_name'
    results = dr.baseball_db_reader(query)
    print(results)

    context = {
        'processes': json.dumps(processes),
        'years_imported': json.dumps(years_imported),
        'teams_processed': json.dumps(teams_processed),
        'stats_generated': json.dumps(stats_generated),
        'recent_10': json.dumps(recent_10),
        'recent_10_min_time': json.dumps(min_time),
        'recent_10_max_time': json.dumps(max_time),
        'recent_10_max_elapsed': max_time_elapsed,
        'error_rate': error_rate
    }

    return render(request, 'pages/jobsDashboard.html', context)