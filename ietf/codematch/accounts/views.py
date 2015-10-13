from django.shortcuts import get_object_or_404, render

from ietf.codematch import constants

from django.db.models import Count

from django.http import HttpResponseRedirect

from ietf.codematch.matches.models import CodingProject

from ietf.codematch.helpers.utils import (render_page, is_user_allowed, clear_session, get_user)

import debug

def index(request):
    return render_to_response('codematch/index.html', context_instance=RequestContext(request))

def register(request):
    return HttpResponseRedirect('/accounts/create/')

def profile(request):
    return HttpResponseRedirect('/accounts/profile/')

def top_coders(request):
    codings = CodingProject.objects.annotate(count=Count('coder'))
    codes = []
    coders   = []
    dict = {}
    for code in codings:
        if code.coder.name not in coders:
            coders.append(code.coder.name)
            codes.append(code)
            dict[code.coder.name] = code
        else:
            c = dict[code.coder.name]
            c.count += 1
    codes = sorted(codes, key=lambda code: code.count, reverse=True)
    return render_page(request, constants.TEMPLATE_TOPCODERS, {
        'codes': codes,
    })