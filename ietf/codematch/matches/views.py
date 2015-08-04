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
from ietf.doc.models import DocAlias, Document

from ietf.codematch.matches.forms import SearchForm, ProjectContainerForm, DocNameForm, CodingProjectForm
from ietf.codematch.matches.models import ProjectContainer, CodingProject
from ietf.codematch.requests.models import CodeRequest

import debug                            

def showlist(request):
    """List all ProjectContaineres by Title"""
    
    project_containers = ProjectContainer.objects.order_by('creation_date')[:20]
    codings            = CodingProject.objects.all()
    return render(request, "codematch/matches/list.html", {
            'projectcontainers' : project_containers,
            'codings'           : codings
    })

def show(request, pk, ck):
    """View individual Codematch Project and Add Document and Implementation"""
    
    project_container = get_object_or_404(ProjectContainer, id=pk)
    coding            = get_object_or_404(CodingProject,    id=ck)
    docs              = project_container.docs.select_related()
    doc_form          = DocNameForm()

    if request.method == 'POST':
       doc_name=request.POST.get("name")

       if doc_name:
          doc = DocAlias.objects.get( name = doc_name )
          project_container.docs.add(doc)
          project_container.save()
          return HttpResponseRedirect('/codematch/matches/'+str(pk)+'/'+str(ck))
      
       else:
          print "Invalid doc" #reload page

    return render(request, "codematch/matches/show.html",  {
        'projectcontainer': project_container,
        'coding'          : coding,
        'docs'            : docs,
        'docform'         : doc_form
    })


def search(request):
    search_type = request.GET.get("submit")
    if search_type:
        form = SearchForm(request.GET)
        docs = None
        project_containers = []
        template = "codematch/matches/list.html"
        
        codings = CodingProject.objects.all()
        
        # get query field
        query = ''
        if request.GET.get(search_type):
            query = request.GET.get(search_type)

        if query :

            # Search by ProjectContainer Title or description
            if search_type == "title":
                project_containers =  ProjectContainer.objects.filter(title__icontains=query) | ProjectContainer.objects.filter(description__icontains=query) 

            elif search_type == "protocol":
                project_containers = ProjectContainer.objects.filter(protocol__icontains=query) 

            elif search_type == "coder":
                # review this
                project_containers = ProjectContainer.objects.filter(codings__coder__name__icontains=query).distinct()
                codings            = CodingProject.objects.filter(coder__name__icontains=query)

            # Document list with a Codematch project
            elif search_type == "doctitle":
                project_containers = ProjectContainer.objects.filter(docs__name__icontains=query)

            else:
                raise Http404("Unexpected search type in ProjectContainer query: %s" % search_type)

            return render(request, template, {
                "projectcontainers" : project_containers,
                "codings"           : codings,
                "docs"              : docs,
                "form"              : form,
            })

        return HttpResponseRedirect(request.path)

    else:
        form = SearchForm()
        return render(request, "codematch/matches/search.html", { "form" : form })


@login_required(login_url='/codematch/accounts/login')
def new(request, pk=""):
    """ New CodeMatch Entry """
    
    proj_form = modelform_factory(ProjectContainer,form=ProjectContainerForm)
    code_form = modelform_factory(CodingProject,form=CodingProjectForm)
    
    project_container = None
    if pk != "": #Already exists project container
        project_container = get_object_or_404(ProjectContainer, id=pk)
    
    if request.method == 'POST':
       
       project = None
       if project_container == None:
           new_project = ProjectContainerForm(request.POST)
           if new_project.is_valid():
              project = new_project.save()
       else:
           project = project_container
       
       new_coding  = CodingProjectForm(request.POST)
       
       if project != None and new_coding.is_valid():
          coding                   = new_coding.save(commit=False)
          coding.coder             = Person.objects.get(user=request.user)
          coding.save()
          project.codings.add(coding)
          project.save()
          return HttpResponseRedirect('/codematch/matches/'+str(project.id)+'/'+str(coding.id))
      
       else:
          print "Some form is not valid"

    return render(request, 'codematch/matches/new.html', {
        'projform'         : proj_form,
        'codeform'         : code_form,
        'projectcontainer' : project_container,
        'pk'               : pk
    })

