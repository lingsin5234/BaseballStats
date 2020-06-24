"""appsetup URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path

from baseball import views as baseball_vw

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^$', baseball_vw.project_markdown),
    # re_path(r'^runJobs/', baseball_vw.run_jobs_view),
    re_path(r'^viewStats/', baseball_vw.stats_view),
    re_path(r'^project/', baseball_vw.project_markdown),
    re_path(r'^jobs-dashboard/', baseball_vw.jobs_dashboard),
    re_path(r'ajax/load-teams/', baseball_vw.load_teams, name='ajax_load_teams'),
    re_path(r'stat_results', baseball_vw.StatsResults.as_view(), name='api_get_stats'),
    re_path(r'flowchart/', baseball_vw.process_flowchart)
]
