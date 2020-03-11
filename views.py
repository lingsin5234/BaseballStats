from django.shortcuts import render
from django.forms.models import model_to_dict
import json
from flask import jsonify
from django.core.serializers.json import DjangoJSONEncoder
from .models import StatCollect
from .oper import db_setup as dbs
from .oper import import_retrosheet as ir
from .oper import process_imports as pi
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
# from .apps import baseball
from .forms import GetYear, ProcessTeam


# main views
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

    return render(request, 'viewStats.html', context)


# run jobs View
def run_jobs_view(request):

    c = dbs.engine.connect()
    form_import = GetYear()
    form_process = ProcessTeam()

    if request.method == 'POST' and 'get_team' in request.POST:
        form = ProcessTeam(request.POST)
        if form.is_valid():
            team = request.POST['get_team']
            year = request.POST['process_year']
            pi.process_data_single_team(year, team)
            print("Processed", team, "for", year)
    else:
        form = GetYear(request.POST)
        if form.is_valid():
            ir.import_data(request.POST['get_year'])
            print("Imported", request.POST['get_year'])

    query = "SELECT * FROM process_log"
    results = c.execute(query).fetchall()
    results = [dict(row) for row in results]

    context = {
        'results': json.dumps(results),
        'form_import': form_import,
        'form_process': form_process
    }

    return render(request, 'pages/runJobs.html', context)
