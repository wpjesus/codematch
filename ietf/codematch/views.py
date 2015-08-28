from django.shortcuts import get_object_or_404

from ietf.codematch.helpers.utils import (render_page)

import debug

def index(request):
    return render_page(request, "codematch/index.html", {})

def about(request):
    return render_page(request, "codematch/about.html", {})