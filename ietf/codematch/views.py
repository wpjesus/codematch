from django.shortcuts import get_object_or_404

from django.http import HttpResponseRedirect

from ietf.codematch.helpers.utils import (render_page)

from django.conf import settings

import debug

def index(request):
    return render_page(request, "codematch/index.html", {})

def about(request):
    return render_page(request, "codematch/about.html", {})

def back(request):
    
    template = "/codematch/index"
    
    if "previous_template" in request.session:
        template = request.session["previous_template"]
    
    return HttpResponseRedirect( settings.CODEMATCH_PREFIX + template )