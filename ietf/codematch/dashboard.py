from ietf.codematch import constants
from ietf.codematch.matches.models import ProjectContainer, CodingProject
from ietf.person.models import Person

from random import randint
import datetime


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