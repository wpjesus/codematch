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
from ietf.codematch.matches.models import ProjectContainer, CodingProject
from ietf.codematch.requests.models import CodeRequest

import debug                            

def about(request):
    return render(request, "codematch/matches/about.html", {})

def index(request):
    return render(request, "codematch/matches/index.html", {})

def showlist(request):
    """List all ProjectContaineres by Title"""
    project_containers = ProjectContainer.objects.order_by('creation_date')[:20]
    return render(request, "codematch/matches/list.html", {
            'projectcontainers' : project_containers
    })


def show(request,pk):
    """View individual Codematch Project and Add Document and Implementation"""
    doc_form = DocNameForm()
    coding_form = modelform_factory(CodingProject,form=CodingProjectForm)
    project_container = get_object_or_404(ProjectContainer, id=pk)
    docs = project_container.docs.select_related()
    codings = CodingProject.objects.filter(project_container = pk)

    if request.method == 'POST':
       doc_name=request.POST.get("name")
       code_form=coding_form(request.POST)

       if doc_name:
          print doc_name, project_container.id
          doc = DocAlias.objects.get( name = doc_name )
          project_container.docs.add(doc)
          project_container.save()
          return HttpResponseRedirect('/codematch/matches/'+str(pk))

       elif code_form.is_valid():
          new_code=code_form.save(commit=False)
          new_code.project_container=project_container #TODO
          new_code.save()
          return HttpResponseRedirect('/codematch/matches/'+str(pk))

       else:
          print "Invalid Entry"

    return render(request, "codematch/matches/show.html",  {
        'projectcontainer': project_container,
        'docs' : docs,
        'codings' : codings,
        'docform' : doc_form,
        'codeform' : coding_form,
        'pk' : pk,
    })


def search(request):
    search_type = request.GET.get("submit")
    if search_type:
        form = SearchForm(request.GET)
        docs = None
        project_containers = []
        template = "codematch/matches/list.html"
    
        # get query field
        query = ''
        if request.GET.get(search_type):
            query = request.GET.get(search_type)

        if query :

            # Search by ProjectContainer Title or description
            if search_type == "title":
                project_containers =  ProjectContainer.objects.filter(Title__icontains=query) | ProjectContainer.objects.filter(Description__icontains=query) 

            elif search_type == "protocol":
                project_containers = ProjectContainer.objects.filter(protocol__icontains=query) 

            elif search_type == "person":
                project_containers = ProjectContainer.objects.filter(Person__name__icontains=query) 

            # Document list with a Codematch project
            elif search_type == "doctitle":
                project_containers = ProjectContainer.objects.filter(docs__name__icontains=query)

            else:
                raise Http404("Unexpected search type in ProjectContainer query: %s" % search_type)

            return render(request, template, {
                "q": query,
                "projectcontainers": project_containers,
                "docs": docs,
                "form":form,
            })

        return HttpResponseRedirect(request.path)

    else:
        form = SearchForm()
        return render(request, "codematch/matches/search.html", {"form":form })


def new(request):
    """ New ProjectContainer Entry """
    form = modelform_factory(ProjectContainer,form=ProjectContainerForm)
    if request.method == 'POST':
       project = ProjectContainerForm(request.POST)
       if project.is_valid():
          project.person = Person.objects.filter(user=request.user.id)
          project_container = project.save()
          return HttpResponseRedirect('/codematch/matches/'+str(projectcontainer.id))
       else:
          print "Form is not valid"

    return render(request, 'codematch/matches/new.html', {'formset': form})

