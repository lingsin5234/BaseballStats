from django.shortcuts import render
from django.forms.models import model_to_dict
import json
from django.core.serializers.json import DjangoJSONEncoder
from .models import StatCollect


# main views
def stats_view(request):
    pull_stats = StatCollect.objects.all()
    stats = []
    for p in pull_stats:
        add = model_to_dict(p)
        stats.append(add)

    context = {
        'stats': json.dumps(stats, cls=DjangoJSONEncoder)
    }

    return render(request, 'viewStats.html', context)
