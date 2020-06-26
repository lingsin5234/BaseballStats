from django.shortcuts import render
from django.forms.models import model_to_dict
import json
from flask import jsonify
from django.core.serializers.json import DjangoJSONEncoder
from .models import StatCollect, JobRequirements
from .oper import db_setup as dbs
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

'''
API Section
'''
from rest_framework import views
from rest_framework.response import Response
from .serializers import StatSerializer


# API View for getting Stats Results table
class StatsResults(views.APIView):

    # get request
    def get(self, request):

        # get batting cols and pop the columns not being displayed
        viewer_col = gv.bat_stat_types.copy()
        viewer_col.pop('PID')
        viewer_col.pop('YEAR')

        # get the keys and values, then add in name to the viewer_col
        query_col = ['player_nm'] + list(viewer_col.values())
        post_col_keys = ['NAME'] + list(viewer_col.keys())
        viewer_col['NAME'] = 'player_nm'  # this way the order for will remain the same

        # read from database; || is concatenate in sqlite!
        query = "SELECT DISTINCT {} FROM batting b " \
                    .format(", ".join(query_col).replace("team_name", "pyts.team_name")
                            .replace("player_nm", "(first_name || ' ' || last_name) as player_nm")) + \
                " JOIN player_year_team pyts ON b.pyts_id = pyts.Id JOIN players p ON " + \
                "pyts.player_id=p.player_id AND pyts.team_name = p.team_id AND pyts.data_year = p.data_year " + \
                "WHERE pyts.team_name='{}' AND pyts.data_year={} " \
                    .format(str(request.GET['team']), str(request.GET['year'])) + "ORDER BY rbis desc"
        temp = dr.baseball_db_reader(query)

        # because `temp` is NOT a dictionary we need to convert it!
        post_col = post_col_keys
        results = []
        for t in temp:
            add = dict(zip(post_col, t))
            add['NAME'] = add['NAME'].replace('"', '')  # replace the extra '"' if there.
            results.append(add)

        data_output = StatSerializer(results, many=True).data

        return Response(data_output)


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


# load drop-down teams based on year
def load_teams(request):

    # request.GET['year'] and request.GET.get('year') work the same?
    # print("Load GET YEAR: ", request.GET['year'])
    year = request.GET['year']
    teams = chk.get_team_choices2(year)
    # print("Load Teams: ", teams)
    team_choices = [r for (r, r) in teams]  # break the tuple
    # print("Load Teams View: ", team_choices)

    return render(request, 'partials/teams_dropdown_options.html', {'teams': team_choices})


# view stats
def stats_view(request):

    # get the year and team choices then grab the ViewStats Form
    year_choices = chk.get_year_choices2()
    # team_choices = [('---', '---')]  ## remove
    team_choices = chk.get_team_choices2("2019")
    form_view_stats = ViewStats(year_choices, team_choices, initial={'form_type': 'view_stats'})

    # get batting cols and pop the columns not being displayed
    viewer_col = gv.bat_stat_types.copy()
    viewer_col.pop('PID')
    viewer_col.pop('YEAR')

    # get the keys and values, then add in name to the viewer_col
    query_col = ['player_nm'] + list(viewer_col.values())
    post_col_keys = ['NAME'] + list(viewer_col.keys())
    viewer_col['NAME'] = 'player_nm'  # this way the order for will remain the same

    # read from database; || is concatenate in sqlite!
    query = "SELECT DISTINCT {} FROM batting b " \
            .format(", ".join(query_col).replace("team_name", "pyts.team_name")
                    .replace("player_nm", "(first_name || ' ' || last_name) as player_nm")) + \
        " JOIN player_year_team pyts ON b.pyts_id = pyts.Id JOIN players p ON " + \
        "pyts.player_id=p.player_id AND pyts.team_name = p.team_id AND pyts.data_year = p.data_year " + \
        "WHERE pyts.team_name='{}' AND pyts.data_year={} " \
            .format('ANA', 2019) + "ORDER BY rbis desc"
    # print(query)
    temp = dr.baseball_db_reader(query)
    # print(temp)

    # because `temp` is NOT a dictionary we need to convert it!
    post_col = post_col_keys
    results = []
    for t in temp:
        add = dict(zip(post_col, t))
        add['NAME'] = add['NAME'].replace('"', '')  # replace the extra '"' if there.
        results.append(add)
    # print(results)

    # change heading
    heading = "Batting Stats for ANA in 2019"

    # change columns into ajax format for the DataTable.js
    ajax_col = []
    for col in post_col:
        ac = {'data': col, 'title': col}
        ajax_col.append(ac)
    # print(ajax_col)

    # query_col -- dict of post_col vs column desc
    query_col = [q.replace('_', ' ') for q in query_col]
    col_dict = dict(zip(post_col, query_col))
    # print(col_dict)

    context = {
        'form_view_stats': form_view_stats,
        'post_col': ajax_col,
        'col_dict': col_dict
    }

    return render(request, 'pages/viewStats.html', context)


# run jobs View -- REMOVED 20200522


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
    all_years.sort()
    all_years.reverse()
    num_teams_array = []
    for y in all_years:
        num_teams = chk.check_teams(str(y), 'total_num_teams')
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
        for m in reversed(range(missing_years)):
            num_teams_array[len_index-m]['num_teams'] = 0
            teams_processed.append(num_teams_array[len_index-m])
    # print(teams_processed)

    # teams that have stats generated -- by year
    query = "SELECT data_year, COUNT(process_name) FROM process_log WHERE process_name LIKE 'stat_processor%' "
    query += "GROUP BY data_year ORDER BY data_year desc"
    results = dr.baseball_db_reader(query)

    # for each row (tuple), sort and add columns
    stats_generated = []
    for r in results:
        stats_generated.append(dict(zip(['data_year', 'processes'], r)))

    # go thru and divide teams/processed by total num of teams
    done_years = []
    stat_cats = ['batting', 'fielding', 'pitching']
    for s in stats_generated:
        year = s['data_year']
        if int(s['data_year']) == year:
            for n in stat_cats:
                s['processes'] = s['processes'] / len(stat_cats)
                # also check if the year is completed
                if s['processes'] == 1:
                    done_years.append(year)
                # print(t)
                break

    # IF FULLY COMPLETED -- merge them together!
    # first drop the completed
    for i, st in reversed(list(enumerate(stats_generated))):
        # if it's done year, drop it
        if st['processes'] == 1:
            stats_generated.pop(i)

    # then add the completed, merged together, to top of the list
    stats_generated = [{
        'data_year': str(min(done_years)) + '-' + str(max(done_years)),
        'num_teams': 1
    }] + stats_generated

    # adjust the SAME done_years for the teams_processed
    # print(teams_processed)
    for i, st in reversed(list(enumerate(teams_processed))):
        # if it's done year, drop it
        if st['data_year'] in done_years:
            teams_processed.pop(i)

    # then add the completed, merged together, to top of the list
    teams_processed = [{
        'data_year': str(min(done_years)) + '-' + str(max(done_years)),
        'num_teams': 1
    }] + teams_processed

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
    max_time_elapsed = max([val for val in [float(item['Elapsed']) for item in recent_10]])
    # print(max_time_elapsed)

    # find the error rate based on gameplay and GEN STATS
    query = 'SELECT COUNT(*) FROM processing_errors'
    results = dr.baseball_db_reader(query)
    errors = int(results[0][0])

    query = 'SELECT COUNT(*) FROM gameplay'
    results = dr.baseball_db_reader(query)
    total = int(results[0][0])
    success = total - errors

    if total > 0:
        error_rate = {'success': round(100 * success / total, 5)}
        error_rate.update({'error': round(100 * errors / total, 5)})
    else:
        error_rate = {'success': 100}
    # print(error_rate)

    # group team: data hits, rbis, home_runs; MUST GROUP BY YEAR LATER!!
    team_data = []
    query = 'SELECT SUM(hits), SUM(home_runs), SUM(rbis), team_name, data_year FROM batting b '
    query += 'JOIN player_year_team pyts ON b.pyts_id=pyts.Id '
    query += 'GROUP BY team_name, data_year'
    results = dr.baseball_db_reader(query)
    for r in results:
        team_data.append(dict(zip(['hits', 'hrs', 'rbis', 'team_name', 'data_year'], r)))

    if len(results) > 0:
        max_hits = max([val for val in [r['hits'] for r in team_data]])
        max_hrs = max([val for val in [r['hrs'] for r in team_data]])
    else:
        team_data = [{'hits': 0, 'hrs': 0, 'rbis': 0, 'team_name': 'N/A', 'data_year': 'N/A'}]
        max_hits = 0
        max_hrs = 0

    context = {
        'processes': json.dumps(processes),
        'years_imported': json.dumps(years_imported),
        'teams_processed': json.dumps(teams_processed),
        'stats_generated': json.dumps(stats_generated),
        'recent_10': json.dumps(recent_10),
        'recent_10_min_time': json.dumps(min_time),
        'recent_10_max_time': json.dumps(max_time),
        'recent_10_max_elapsed': max_time_elapsed,
        'error_rate': error_rate,
        'team_data': team_data,
        'max_hits': max_hits,
        'max_hrs': max_hrs
    }

    return render(request, 'pages/jobsDashboard.html', context)


# show the process flowchart of baseball project
def process_flowchart(request):

    context = {

    }

    return render(request, 'pages/flowchart.html', context)
