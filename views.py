from django.shortcuts import render
from django.forms.models import model_to_dict


# main views
def stats_view(request):
    pull_stats = StatCollect.objects.all()
    stats = []
    for p in pull_stats:
        add = model_to_dict(pull_stats)
        stats.append(add)

    context = {
        'stats': json.dumps(stats, cls=DjangoJSONEncoder)
    }

    return render(request, 'viewStats.html', context)
