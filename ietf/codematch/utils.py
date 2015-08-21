from django.shortcuts import get_object_or_404, render

from ietf.person.models import Person, Alias
from ietf.codematch.matches.models import ProjectContainer, CodingProject
from ietf.codematch.requests.models import CodeRequest

import debug

def is_user_allowed(user, permission):
    return True

def get_menu_arguments(request, dict):
    if request.user.is_authenticated():
        user = Person.objects.get(user=request.user)
        my_codings = CodingProject.objects.filter( coder = user )
        projects_my_own = ProjectContainer.objects.filter( owner = user )
        projects_my_mentoring = ProjectContainer.objects.filter( code_request__mentor = user )
        dict["mycodings"] = my_codings
        dict["projectsowner"] = projects_my_own
        dict["projectsmentoring"] = projects_my_mentoring
        # TODO: review this, add here others permissions
        dict["canaddrequest"] = is_user_allowed(user, "canaddrequest")
        dict["canaddcoding"]  = is_user_allowed(user, "canaddcoding")
        dict["ismentor"]      = is_user_allowed(user, "ismentor")
        
        alias = Alias.objects.filter( person = user )
        
        if alias:
            alias_name = alias[0].name
        else:
            alias_name = user.name
            
        dict["username"] = alias_name
        
    return dict

def render_page(request, template, dict = {}):
    return render(request, template, get_menu_arguments(request,dict))
