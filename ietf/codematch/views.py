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


def dashboard(request):
    
    modules = ['codematch/widgets/all_matches.html', 'codematch/widgets/my_matches.html', 
               'codematch/widgets/my_requests.html']
    colors = ['progress-bar progress-bar-info', 'progress-bar progress-bar-danger',
              'progress-bar progress-bar-warning']
    
    user = get_user(request)
    
    total_items = randint(1, 3)
    items = []
    #for i in range(0,total_items):
    #    items.append(modules[randint(0, 2)])
    items.append(modules[0])
    items.append(modules[1])
    items.append(modules[2])
    
    keys = {'items': items}
    
    codings = []
    my_codings = []
    my_requests = []
    all_projects = ProjectContainer.objects.all()
    all_codings = CodingProject.objects.order_by('-id')[:3]
    for coding in all_codings:
        for project in all_projects:
            if coding in project.codings.all():
                coder = Person.objects.using('datatracker').get(id=coding.coder)
                codings.append((coding, project, coder))
                break
    
    all_projects = ProjectContainer.objects.exclude(code_request__isnull=True).filter(owner=user.id)[:3]
    for project in all_projects:
        my_requests.append(project)
        
    all_codings = CodingProject.objects.filter(coder=user.id)[:3]
    for coding in all_codings:
        my_codings.append((coding, str(datetime.datetime.now().date()), str(randint(0, 100)), 
                          colors[randint(0, 2)]))
        
    keys['codings'] = codings    
    keys['my_codings'] = my_codings
    keys['my_requests'] = my_requests
    
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
