from django.shortcuts import render

# main views
def stats_view(request):
    pull_stats = StatCollect.objects.all()

    context = {
        'stats': pull_stats
    }

    return render(request, 'viewStats.html', context)
