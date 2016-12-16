from ietf.codestand import constants
from django.db.models import Count
from django.http import HttpResponseRedirect, Http404
from ietf.codestand.matches.models import CodingProject, ProjectContainer
from ietf.codestand.helpers.utils import (render_page, get_user)
from ietf.person.models import Person
from django.conf import settings


def index(request):
    return render_page(request, 'codestand/index.html')


def register(request):
    return HttpResponseRedirect(settings.CODESTAND_PREFIX + '/accounts/create/')


def profile(request, user=None):
    if user is None:
        current_user = get_user(request)
        if current_user is None:
            raise Http404
        else:
            user = current_user.id
    coder = Person.objects.using('datatracker').get(id=user)
    projects = ProjectContainer.objects.filter(owner=user)
    codings = CodingProject.objects.filter(coder=user)
    return render_page(request, constants.TEMPLATE_PROFILE, {
        'coder': coder,
        'projects': projects,
        'codings': codings,
    })


def top_coders(request):
    codings = CodingProject.objects.annotate(count=Count('coder'))
    codes = []
    coders = []
    topcoders = []
    dict_code = {}
    ids = []
    for coding in codings:
        ids.append(coding.coder)
    ids = list(set(ids))
    all_coders = list(Person.objects.using('datatracker').filter(id__in=ids).values_list('id', 'name'))
    for code in codings:
        if code.coder not in coders:
            coders.append(code.coder)
            codes.append(code)
            dict_code[code.coder] = code
        else:
            c = dict_code[code.coder]
            c.count += 1
    codes = sorted(codes, key=lambda c: c.count, reverse=True)
    for cd in codes:
        coder = 'None'
        for id, name in all_coders:
            if cd.coder == id:
                coder = name
        topcoders.append((cd.count, coder))
    return render_page(request, constants.TEMPLATE_TOPCODERS, {
        'topcoders': topcoders,
    })
