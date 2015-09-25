from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseRedirect

from django.conf import settings

import debug

def index(request):
    return render_to_response('codematch/index.html', context_instance=RequestContext(request))

def register(request):
    return HttpResponseRedirect(settings.CODEMATCH_PREFIX + '/accounts/create/')

def profile(request):
    return HttpResponseRedirect(settings.CODEMATCH_PREFIX + '/accounts/profile/')
