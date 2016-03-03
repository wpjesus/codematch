from django.http import HttpResponseRedirect
from ietf.codematch.helpers.utils import (render_page)
from ietf.codematch import constants

def index(request):
    return render_page(request, constants.TEMPLATE_INDEX)


def about(request):
    return render_page(request, constants.TEMPLATE_ABOUT)


def back(request):
    template = "/codematch/index"

    if "previous_template" in request.session:
        template = request.session["previous_template"]

    return HttpResponseRedirect(template)
