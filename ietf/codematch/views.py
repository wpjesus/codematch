from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from ietf.codematch.helpers.utils import (render_page, get_user)
from ietf.codematch import constants
from ietf.codematch.matches.models import ProjectContainer, CodingProject
from ietf.person.models import Person

from random import randint
import datetime


def index(request):
    return render_page(request, constants.TEMPLATE_INDEX)


def about(request):
    return render_page(request, constants.TEMPLATE_ABOUT)


def get_all_matches(user, keys):
    codings = []
    all_projects = ProjectContainer.objects.all()
    all_codings = CodingProject.objects.order_by('-id')[:3]
    for coding in all_codings:
        for project in all_projects:
            if coding in project.codings.all():
                coder = Person.objects.using('datatracker').get(id=coding.coder)
                codings.append((coding, project, coder))
                break
                
    keys['all_matches'] = codings
    
    return constants.WIDGET_ALL_MATCHES


def get_my_requests(user, keys):
    my_requests = []
    all_projects = ProjectContainer.objects.exclude(code_request__isnull=True).filter(owner=user.id)[:3]
    for project in all_projects:
        my_requests.append(project)
        
    keys['my_requests'] = my_requests
    
    return constants.WIDGET_MY_REQUESTS


def get_my_matches(user, keys):
    colors = ['progress-bar progress-bar-info', 'progress-bar progress-bar-danger',
              'progress-bar progress-bar-warning']
    
    my_codings = []    
    all_codings = CodingProject.objects.filter(coder=user.id)[:3]
    for coding in all_codings:
        my_codings.append((coding, datetime.datetime.now().date(), randint(0, 100), 
                          colors[randint(0, 2)]))
            
    keys['my_matches'] = my_codings
    
    return constants.WIDGET_MY_MATCHES
    
    
def dashboard(request, rand=None):
    
    methods = [get_my_matches, get_my_requests, get_all_matches]
    
    user = get_user(request)
    keys = {}
    items = []
    if rand is not None:
        for i in range(randint(1,3)):
            items.append(methods[randint(0, 2)](user, keys))
    else:
        for i in range(0, len(methods)):
            items.append(methods[i](user, keys))
    
    keys['items'] = items
    
    return render_page(request, constants.TEMPLATE_DASHBOARD, keys)


def back(request):
    template = "/codematch/"

    if "previous_template" in request.session:
        template = request.session["previous_template"]

    return HttpResponseRedirect(template)


def handler500(request):
    #TODO: Rever para filtrar apenas o erro especifico 500
    sync()
    print 'updated local database'
    #  return render_page(request, constants.TEMPLATE_ERROR_500)
    return render_page(request, constants.TEMPLATE_INDEX)


def handler404(request):
    return render_page(request, constants.TEMPLATE_ERROR_404)


def sync():    
    """all_persons = Person.objects.using('datatracker')
    codematch_persons = Person.objects.using('default').all().values_list('id', flat=True)
    
    for person in all_persons:
        if person.id not in codematch_persons:
            try:
                person.save()
            except:
                pass"""
    
    all_users = User.objects.using('datatracker').all()
    codematch_users = User.objects.using('default').all().values_list('id', flat=True)
    for us in all_users:
        if us.id not in codematch_users:
            try:
                us.save()
            except:
                pass
