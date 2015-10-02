from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseRedirect

import debug

def index(request):
    return render_to_response('codematch/index.html', context_instance=RequestContext(request))

def register(request):
    return HttpResponseRedirect('/accounts/create/')

def profile(request):
    return HttpResponseRedirect('/accounts/profile/')