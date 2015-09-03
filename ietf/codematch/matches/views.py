import datetime
from django.shortcuts import get_object_or_404

from django import forms
from django.forms import CharField
from django.forms import ModelForm
from django.forms.models import modelform_factory, inlineformset_factory

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect

from django.contrib.auth.decorators import login_required

from ietf.group.models import Group
from ietf.person.models import Person

from ietf.codematch.matches.forms import SearchForm, ProjectContainerForm, CodingProjectForm, LinkImplementationForm
from ietf.codematch.matches.models import ProjectContainer, CodingProject, Implementation
from ietf.codematch.requests.models import CodeRequest

from ietf.codematch.helpers.utils import (render_page, is_user_allowed)

from django.conf import settings

import debug                            

def show_list(request):
    """ List all ProjectContaineres by Title """
    
    project_containers = ProjectContainer.objects.order_by('creation_date')[:20]
    codings            = CodingProject.objects.all()
	
    return render_page(request, "codematch/matches/list.html", {
            'projectcontainers' : project_containers,
            'codings'           : codings
    })

def show(request, pk, ck):
    """ Show individual Codematch Project and Add Implementation """
    
    project_container = get_object_or_404(ProjectContainer, id=pk)
    coding            = get_object_or_404(CodingProject,    id=ck)
    #links             = coding.links.all()
    link_form         = LinkImplementationForm()
    
    if request.user.is_authenticated():
        user        = Person.objects.get( user = request.user )
        is_my_match = coding.coder == user

	# TODO: Migrate to 'new'
    if request.method == 'POST':
       link_to_implementation = LinkImplementationForm(request.POST)
      
	   # Adding new implementation (Review this attribute name)
       if link_to_implementation.is_valid():
          link = link_to_implementation.save()
          
          coding.links.add(link)
          coding.save()
          return HttpResponseRedirect( settings.CODEMATCH_PREFIX + '/codematch/matches/' + str(pk) + '/' + str(ck) )

    return render_page(request, "codematch/matches/show.html",  {
        'projectcontainer': project_container,
        'coding'          : coding,
        'linkform'        : link_form,
        'mymatch'         : is_my_match
    })

def search(request):
    """ Shows the list of projects, filtering by some query (title, protocol, coder or doctitle) """
    
    search_type = request.GET.get("submit")
    if search_type:
        form = SearchForm(request.GET)
        docs = None
        project_containers = []
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
            # Document list with a Codematch project (MOVE IT TO CODEREQUESTS)
            elif search_type == "doctitle":
                project_containers = ProjectContainer.objects.filter(docs__name__icontains=query)

            else:
                raise Http404("Unexpected search type in ProjectContainer query: %s" % search_type)

            return render_page(request, "codematch/matches/list.html", {
                "projectcontainers" : project_containers,
                "codings"           : codings,
                "docs"              : docs,
                "form"              : form,
            })

        return HttpResponseRedirect(request.path)

    else:
        return render_page(request, "codematch/matches/search.html", { "form" : SearchForm() })

@login_required(login_url = settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def new(request, pk=""):
    ''' New CodeMatch Entry
    When user presses 'Associate new project' there is a Project Container
    associated, then you need reuse this information in the form '''
    
    proj_form = modelform_factory(ProjectContainer,form=ProjectContainerForm)
    code_form = modelform_factory(CodingProject,form=CodingProjectForm)

    project_container = None
    if pk != "": # Already exists project container (via CodeRequests)
        project_container = get_object_or_404(ProjectContainer, id=pk)
            
    if request.method == 'POST':
    	project = None
    	# If there wasn't associated Project Container, must create a new one. Functionality used to legacy RFC.
    	if project_container == None:
    		new_project = ProjectContainerForm(request.POST) 
    		
    	if new_project.is_valid():
    		project = new_project.save() # Create new
    	else:
    		project = project_container # Update only
    
    	new_coding  = CodingProjectForm(request.POST)
    
    	if project != None and new_coding.is_valid():
    		coding                   = new_coding.save(commit=False)
    		coding.coder             = Person.objects.get( user=request.user )
    		coding.save()
    		project.codings.add(coding)
    		project.save()
    
    		return HttpResponseRedirect( settings.CODEMATCH_PREFIX + '/codematch/matches/' + str(project.id) + '/' + str(coding.id) )
    
    return render_page(request, 'codematch/matches/new.html', {
    'projform'         : proj_form,
    'codeform'         : code_form,
    'projectcontainer' : project_container,
    'pk'               : pk
    })

