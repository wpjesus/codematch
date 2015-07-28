import datetime
from django.shortcuts import get_object_or_404, render

from django import forms
from django.forms import CharField
from django.forms import ModelForm
from django.forms.models import modelform_factory, inlineformset_factory

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect

from ietf.group.models import Group
from ietf.person.models import Person
from ietf.doc.models import DocAlias, Document

from ietf.codematch.matches.forms import SearchForm, ProjectContainerForm, DocNameForm, CodingProjectForm
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
    return render(request, "codematch/requests/search.html", {})

def show(request,pk):
    """View individual Codematch Project and Add Document and Implementation"""
    project_container = get_object_or_404(ProjectContainer, id=pk)

    return render(request, "codematch/requests/show.html",  {
        'projectcontainer': project_container,
    })


def new(request):
    """ New CodeRequest Entry """
    proj_form = modelform_factory(ProjectContainer,form=ProjectContainerForm)
    code_form = modelform_factory(CodeRequest,form=CodeRequestForm)
    if request.method == 'POST':
       new_project = ProjectContainerForm(request.POST)
       new_request = CodeRequestForm(request.POST)
       if new_project.is_valid() and new_request.is_valid():
          # TODO: review this
          #new_request.mentor = Person.objects.filter(user=request.user.id)
          code_request              = new_request.save()
          project                   = new_project.save(commit=False)
          project.code_request      = code_request
          project.save()
          return HttpResponseRedirect('/codematch/requests/'+str(code_request.id))
       else:
          print "Some form is not valid"

    return render(request, 'codematch/requests/new.html', {
        'projform' : proj_form,
        'reqform' : code_form,
    })

