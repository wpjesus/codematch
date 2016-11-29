from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from ietf.codestand.helpers.utils import (render_page)
from ietf.codestand import constants


def index(request):
    sync(request)
    return render_page(request, constants.TEMPLATE_INDEX)


def about(request):
    return render_page(request, constants.TEMPLATE_ABOUT)


def back(request):
    template = "/codestand/"

    if "previous_template" in request.session:
        template = request.session["previous_template"]

    return HttpResponseRedirect(template)


def handler500(request):
    # TODO: Review this to filter only the specific error
    print 'updated local database'
    sync(request)


def handler404(request):
    return render_page(request, constants.TEMPLATE_ERROR_404)


def sync(request):
    """ :param request: """
    
    all_users = User.objects.using('datatracker').all()
    codestand_users = User.objects.using('default').all().values_list('id', flat=True)

    for us in all_users:
        if us.id not in codestand_users:
            try:
                us.save()
            except:
                pass
    #return render_page(request, constants.TEMPLATE_ERROR_500)
