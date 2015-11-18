from ietf.codematch import constants
from django.db.models import Count
from django.http import HttpResponseRedirect
from ietf.codematch.matches.models import CodingProject
from ietf.codematch.helpers.utils import (render_page)
from django.conf import settings


def index(request):
    return render_page(request, 'codematch/index.html')

def register(request):
    return HttpResponseRedirect(settings.CODEMATCH_PREFIX + '/accounts/create/')

def profile(request):
    return HttpResponseRedirect(settings.CODEMATCH_PREFIX + '/accounts/profile/')

def top_coders(request):
    codings = CodingProject.objects.annotate(count=Count('coder'))
    codes = []
    coders = []
    dict_code = {}
    for code in codings:
        if code.coder.name not in coders:
            coders.append(code.coder.name)
            codes.append(code)
            dict_code[code.coder.name] = code
        else:
            c = dict_code[code.coder.name]
            c.count += 1
    codes = sorted(codes, key=lambda c: c.count, reverse=True)
    return render_page(request, constants.TEMPLATE_TOPCODERS, {
        'codes': codes,
    })
