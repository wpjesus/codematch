from django.shortcuts import get_object_or_404

from django.http import HttpResponseRedirect

from ietf.codematch.helpers.utils import (render_page)

from django.conf import settings

from ietf.codematch import constants

import debug

def index(request):
    #return render_page(request, "codematch/index.html", {})
	return render_page(request, constants.TEMPLATE_INDEX)
	
def about(request):
    #return render_page(request, "codematch/about.html", {})
	return render_page(request, constants.TEMPLATE_ABOUT)
	
def back(request):
    
    template = "/codematch/index"
    
    if "previous_template" in request.session:
        template = request.session["previous_template"]
    
    # TODO: Need settings.CODEMATCH_PREFIX???
    return HttpResponseRedirect( template )