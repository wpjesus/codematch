from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from ietf.codematch.helpers.utils import (render_page)
from ietf.codematch import constants
from ietf.person.models import Person


def index(request):
    return render_page(request, constants.TEMPLATE_INDEX)


def about(request):
    return render_page(request, constants.TEMPLATE_ABOUT)


def back(request):
    template = "/codematch/"

    if "previous_template" in request.session:
        template = request.session["previous_template"]

    return HttpResponseRedirect(template)

def handler500(request):
    # TODO: Review this to filter only the specific error
    print 'updated local database'
    return sync(request)


def handler404(request):
    return render_page(request, constants.TEMPLATE_ERROR_404)


def sync(request):
    """ :param request: """
    
    all_users = User.objects.using('datatracker').all()
    codematch_users = User.objects.using('default').all().values_list('id', flat=True)
    for us in all_users:
        if us.id not in codematch_users:
            try:
                us.save()
            except:
                pass
    return render_page(request, constants.TEMPLATE_ERROR_500)
