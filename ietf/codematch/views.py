from django.shortcuts import get_object_or_404, render

from ietf.codematch.utils import (get_prefix)

import debug

def index(request):
    return render(request, "codematch/index.html", {})

def about(request):
    return render(request, "codematch/about.html", {})