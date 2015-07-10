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

from ietf.codematch.forms import SearchForm, ProjectContainerForm, DocNameForm, CodingProjectForm
from ietf.codematch.models import ProjectContainer, CodingProject, CodeRequest

import debug                            

def about(request):
    return render(request, "codematch/about.html", {})

def showlist(request):
    """List all ProjectContaineres by Title"""
    projectcontainers = ProjectContainer.objects.order_by('Creation_date')[:20]
    return render(request, "codematch/list.html", {
            'projectcontainers' : projectcontainers
    })


def show(request,pk):
    """View individual Codematch Project and Add Document and Implementation"""
    docform = DocNameForm()
    CodingForm = modelform_factory(CodingProject,form=CodingProjectForm)
    projectcontainer = get_object_or_404(ProjectContainer, id=pk)
    docs = projectcontainer.docs.select_related()
    codings = CodingProject.objects.filter(ProjectContainer = pk)

    if request.method == 'POST':
       docname=request.POST.get("name")
       code_form=CodingForm(request.POST)

       if docname:
          print docname, projectcontainer.id
          doc = DocAlias.objects.get( name = docname )
          projectcontainer.docs.add(doc)
          projectcontainer.save()
          return HttpResponseRedirect('/codematch/'+str(pk))

       elif code_form.is_valid():
          newcode=code_form.save(commit=False)
          newcode.ProjectContainer=projectcontainer
          newcode.save()
          return HttpResponseRedirect('/codematch/'+str(pk))

       else:
          print "Invalid Entry"

    return render(request, "codematch/show.html",  {
        'projectcontainer': projectcontainer,
        'docs' : docs,
        'codings' : codings,
        'docform' : docform,
        'codeform' : CodingForm,
        'pk' : pk,
    })


def search(request):
    search_type = request.GET.get("submit")
    if search_type:
        form = SearchForm(request.GET)
        docs = None
        projectcontainers = []
        template = "codematch/list.html"
    
        # get query field
        q = ''
        if request.GET.get(search_type):
            q = request.GET.get(search_type)

        if q :

            # Search by ProjectContainer Title or description
            if search_type == "title":
                projectcontainers =  ProjectContainer.objects.filter(Title__icontains=q) | ProjectContainer.objects.filter(Description__icontains=q) 

            elif search_type == "protocol":
                projectcontainers = ProjectContainer.objects.filter(protocol__icontains=q) 

            elif search_type == "person":
                projectcontainers = ProjectContainer.objects.filter(Person__name__icontains=q) 

            # Document list with a Codematch project
            elif search_type == "doctitle":
                projectcontainers = ProjectContainer.objects.filter(docs__name__icontains=q)

            else:
                raise Http404("Unexpected search type in ProjectContainer query: %s" % search_type)

            return render(request, template, {
                "q": q,
                "projectcontainers": projectcontainers,
                "docs": docs,
                "form":form,
            })

        return HttpResponseRedirect(request.path)

    else:
        form = SearchForm()
        return render(request, "codematch/search.html", {"form":form })


def new(request):
    """ New ProjectContainer Entry """
    form = modelform_factory(ProjectContainer,form=ProjectContainerForm)
    if request.method == 'POST':
       project = ProjectContainerForm(request.POST)
       if project.is_valid():
          project.person = Person.objects.filter(user=request.user.id)
          projectcontainer = project.save()
          return HttpResponseRedirect('/codematch/'+str(projectcontainer.id))
       else:
          print "Form is not valid"

    return render(request, 'codematch/new.html', {'formset': form})

