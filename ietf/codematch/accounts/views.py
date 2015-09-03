from django.shortcuts import get_object_or_404, render

import debug

def index(request):
    return render_to_response('codematch/index.html', context_instance=RequestContext(request))