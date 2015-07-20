from django.shortcuts import get_object_or_404, render

import debug

def index(request):
    return render(request, "codematch/index.html", {})