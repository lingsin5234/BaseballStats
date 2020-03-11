from django.shortcuts import render
from django.forms.models import model_to_dict
import json
from flask import jsonify
from django.core.serializers.json import DjangoJSONEncoder
from .models import StatCollect
from .oper import db_setup as dbs
from .oper import import_retrosheet as ir
from .oper import process_imports as pi
from .oper import generate_statistics as gs
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
# from .apps import baseball
from .forms import GetYear, ProcessTeam, GenerateStats


# home page
def home_page(request):
    return render(request, 'pages/homepage.html')


# view stats
def stats_view(request):
    # pull_stats = StatCollect.objects.all()
    # stats = []
    # for p in pull_stats:
    #     add = model_to_dict(p)
    #     stats.append(add)
    #
    # context = {
    #     'stats': json.dumps(stats, cls=DjangoJSONEncoder)
    # }

    c = dbs.engine.connect()
    query = "SELECT * FROM process_log"
    results = c.execute(query)

    context = {
        'results': results
    }

    return render(request, 'pages/viewStats.html', context)


# run jobs View
def run_jobs_view(request):

    # DB connect and form initializations
    c = dbs.engine.connect()
    form_import = GetYear(initial={'form_type': 'import_year'})
    form_process = ProcessTeam(initial={'form_type': 'process_team'})
    form_gen_stats = GenerateStats(initial={'form_type': 'gen_stats'})

    if request.method == 'POST':
        if 'team' in request.POST:
            team = request.POST['team']
        year = request.POST['year']
        if request.POST['form_type'] == 'import_year':
            form = GetYear(request.POST)
            if form.is_valid():
                ir.import_data(request.POST['year'])
                print("Imported", request.POST['year'])
                print(request.POST)
            else:
                print(form.errors)
        elif request.POST['form_type'] == 'process_team':
            form = ProcessTeam(request.POST)
            if form.is_valid():
                pi.process_data_single_team(year, team)
                print("Processed", team, "for", year)
                print(request.POST)
            else:
                print(form.errors)
        elif request.POST['form_type'] == 'gen_stats':
            form = GenerateStats(request.POST)
            if form.is_valid():
                gs.generate_stats(year, team)
                print("Imported", request.POST['year'])
                print(request.POST)
            else:
                print(form.errors)
    else:
        # do nothing as initial forms are already declared
        pass

    query = "SELECT * FROM process_log ORDER BY timestamp DESC LIMIT 10"
    results = [dict(row) for row in c.execute(query).fetchall()]

    context = {
        'results': json.dumps(results),
        'form_import': form_import,
        'form_process': form_process,
        'form_gen_stats': form_gen_stats
    }

    return render(request, 'pages/runJobs.html', context)
