import datetime
from django.shortcuts import get_object_or_404, render

from django import forms
from django.forms import CharField
from django.forms import ModelForm
from django.forms.models import modelform_factory, inlineformset_factory

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect

from django.contrib.auth.decorators import login_required

from ietf.group.models import Group
from ietf.person.models import Person

from ietf.codematch.matches.forms import SearchForm, ProjectContainerForm
from ietf.codematch.requests.forms import CodeRequestForm
from ietf.codematch.matches.models import ProjectContainer, CodingProject
from ietf.codematch.requests.models import CodeRequest

import debug                            

def showlist(request):
    """List all CodeRequests by Title"""
    
    project_containers = ProjectContainer.objects.exclude(code_request__isnull=True).order_by('creation_date')[:20]
    return render(request, "codematch/requests/list.html", {
            'projectcontainers' : project_containers
    })         

def search(request):
    search_type = request.GET.get("submit")
    if search_type:
        form               = SearchForm(request.GET)
        project_containers = []
        template           = "codematch/requests/list.html"
    
        # get query field
        query = ''
        if request.GET.get(search_type):
            query = request.GET.get(search_type)

        if query :

            # Search by ProjectContainer Title or description
            if search_type   == "title":
                project_containers  =  ProjectContainer.objects.filter(title__icontains=query) | ProjectContainer.objects.filter(description__icontains=query) 

            elif search_type == "protocol":
                project_containers  =  ProjectContainer.objects.filter(protocol__icontains=query) 

            elif search_type == "mentor":
                project_containers = ProjectContainer.objects.filter(code_request__mentor__name__icontains=query) 

            else:
                raise Http404("Unexpected search type in ProjectContainer query: %s" % search_type)

            return render(request, template, {
                "projectcontainers" : project_containers,
                "form"              : form,
            })

        return HttpResponseRedirect(request.path)

    else:
        form = SearchForm()
        return render(request, "codematch/requests/search.html", { "form" : form })

def show(request,pk):
    """View individual Codematch Project and Add Document and Implementation"""
    
    project_container = get_object_or_404(ProjectContainer, id=pk)
    return render(request, "codematch/requests/show.html",  {
        'projectcontainer': project_container,
    })


@login_required(login_url='/codematch/accounts/login')
def new(request):
    """ New CodeRequest Entry """
    
    proj_form = modelform_factory(ProjectContainer,form=ProjectContainerForm)
    req_form  = modelform_factory(CodeRequest,form=CodeRequestForm)
    
    if request.method == 'POST':
       new_project = ProjectContainerForm(request.POST)
       new_request = CodeRequestForm(request.POST)
       
       if new_project.is_valid() and new_request.is_valid():
          code_request              = new_request.save(commit=False)
          code_request.mentor       = Person.objects.get(user=request.user)
          code_request.save()
          project                   = new_project.save(commit=False)
          project.code_request      = code_request
          project.save()
          return HttpResponseRedirect('/codematch/requests/'+str(project.id))
       else:
          print "Some form is not valid"

    return render(request, 'codematch/requests/new.html', {
        'projform' : proj_form,
        'reqform'  : req_form,
    })

