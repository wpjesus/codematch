import datetime
from django.shortcuts import get_object_or_404

from django import forms
from django.forms.models import modelform_factory

from django.http import Http404, HttpResponseRedirect

from django.contrib.auth.decorators import login_required

from ietf.group.models import Group
from ietf.person.models import Person
from ietf.doc.models import DocAlias, Document

from ietf.codematch.matches.forms import SearchForm, ProjectContainerForm
from ietf.codematch.requests.forms import CodeRequestForm, DocNameForm, TagForm

from ietf.codematch.matches.models import ProjectContainer, CodingProject, ProjectTag
from ietf.codematch.requests.models import CodeRequest

from ietf.codematch.helpers.utils import (render_page, is_user_allowed)

from django.conf import settings

import debug                            

def show_list(request): 
    """ List all CodeRequests """
    
    # TODO: Allow sorting by different parameters (for others templates too)
    # Exclude ProjectContainers that don't have an associated CodeRequest (TODO: Centralize this?)
    project_containers = ProjectContainer.objects.exclude(code_request__isnull=True).order_by('creation_date')[:20]
    
    user = None
    
    if request.user.is_authenticated():
        #(TODO: Centralize this?)
        user = Person.objects.get( user = request.user )
    
    return render_page(request, "codematch/requests/list.html", {
            'projectcontainers' : project_containers,
            'owner'             : user
    }) 

@login_required(login_url = settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def show_my_list(request):
    """ List CodeRequests i've created """
    
    #(TODO: Centralize this?)
    user = Person.objects.get( user = request.user )
    
    # Exclude ProjectContainers that don't have an associated CodeRequest (TODO: Centralize this?)
    project_containers = ProjectContainer.objects.exclude(code_request__isnull=True).filter( owner = user ).order_by('creation_date')[:20]
    
    if not is_user_allowed(user, "iscreator") and project_containers.count() == 0:
        raise Http404
    
    return render_page(request, "codematch/requests/list.html", {
            'projectcontainers' : project_containers,
            'owner'             : user
    })

@login_required(login_url = settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def show_mentoring_list(request):
    """ List CodeRequests i'm mentoring """
    
    #(TODO: Centralize this?)
    user = Person.objects.get( user = request.user )
    
    # Exclude ProjectContainers that don't have an associated CodeRequest (TODO: Centralize this?)
    project_containers = ProjectContainer.objects.exclude(code_request__isnull=True).filter( code_request__mentor = user ).order_by('creation_date')[:20]
    
    # Project must have been mentored by the current user and user must have permission mentor
    if not is_user_allowed(user, "ismentor") and project_containers.count() == 0:
        raise Http404
    
    return render_page(request, "codematch/requests/list.html", {
        'projectcontainers' : project_containers,
        'owner'             : user
    })  

def search(request):
    """ Shows the list of projects, filtering by some query (title, protocol or mentor) """
    
    search_type = request.GET.get("submit")
    if search_type:
    
        # get query field
        query = ''
        if request.GET.get(search_type):
            query = request.GET.get(search_type)
        
        if query:
            
            project_containers = []
            template           = "codematch/requests/list.html"
                    
            if search_type   == "title":
                project_containers  =  ProjectContainer.objects.filter(title__icontains=query) | ProjectContainer.objects.filter(description__icontains=query) 
            
            elif search_type == "protocol":
                project_containers  =  ProjectContainer.objects.filter(protocol__icontains=query) 
            
            elif search_type == "mentor":
                project_containers  = ProjectContainer.objects.filter(code_request__mentor__name__icontains=query) 
            
            else:
                raise Http404("Unexpected search type in ProjectContainer query: %s" % search_type)
            
            return render_page(request, template, {
                "projectcontainers" : project_containers
            })
            
        else:
            return HttpResponseRedirect(request.path)
    
    else:
        form = SearchForm()
        return render_page(request, "codematch/requests/search.html", { 
            "form" : form 
        })

def show(request,pk):
    """ Show individual Codematch Project """
    
    project_container = get_object_or_404(ProjectContainer, id=pk)
    
    areas          = []
    working_groups = []
    tags           = []
    
    # According to model areas and working groups should come from documents
    for doc in project_container.docs.all():
        group = doc.document.group
        if not group.name in working_groups:
            working_groups.append(group.name)
        if group.parent:
            if not group.parent.name in areas:
                areas.append(group.parent.name) # use acronym?
        else:
            areas.append(working_group) 
    
    for tag in project_container.tags.all():
        tags.append(tag.name)
    
    # If the list is empty should display None
    if not areas:
        areas          = ["None"]
    if not working_groups:
        working_groups = ["None"]
    if not tags:
        tags           = ["None"]
    
    return render_page(request, "codematch/requests/show.html",  {
        'projectcontainer': project_container,
        'areas'           : areas,
        'workinggroups'   : working_groups,
        'tags'            : tags
    })


def save_project(request, template, project_container=None):

    # NOTE: Is slow 'cause of the mentors list
    
    # User must have permission to add new CodeRequest
    if not is_user_allowed(request.user, "canaddrequest"):
        raise Http404

    cached_project = None
    cached_request = None
    docs = []
    tags = []
    
    doc_form  = DocNameForm()
    tag_form  = modelform_factory(ProjectTag,form=TagForm)
    
    #(TODO: Centralize this?)
    user = Person.objects.get( user = request.user )
    # TODO: check permission
    is_my_request = is_user_allowed(user, "canadddocuments")

    if 'project_instance' in request.session:
        proj_form = request.session['project_instance']
    else:
        proj_form = ProjectContainerForm()

    if 'request_instance' in request.session:
        req_form = request.session['request_instance']
    else:
        req_form = CodeRequestForm()

    if 'docs' not in request.session:
        request.session['docs'] = []
    else:
        doc_list = request.session["docs"]
        for doc in doc_list:
            docs.append(doc)
            
    if 'tags' not in request.session:
        request.session['tags'] = []
    else:
        tag_list = request.session["tags"]
        for tag in tag_list:
            tags.append(tag)
    
    if project_container != None:
        for doc in project_container.docs.all():
            docs.append(doc)
        for tag in project_container.tags.all():
            tags.append(tag)
    
    if request.method == 'POST':
        
        doc_name = request.POST.get("doc")
        tag      = TagForm(request.POST)
        
        if project_container != None:
            new_proj = ProjectContainerForm(request.POST, instance=project_container)
            new_req  = CodeRequestForm(request.POST, instance=project_container.code_request)
        else:
            new_proj = ProjectContainerForm(request.POST)
            new_req  = CodeRequestForm(request.POST)

        # Adding document to the ProjectContainer
        if doc_name:
            selected_document = DocAlias.objects.filter( name = doc_name )
            if selected_document:
                new_doc  = selected_document[0]
                doc_list = request.session["docs"]
                doc_list.append(new_doc)
                docs.append(new_doc)
                request.session["docs"] = doc_list
            
        # Adding new tag to the ProjectContainer
        elif tag.is_valid():
            new_tag  = tag.save(commit=False)
            tag_list = request.session["tags"]
            tag_list.append(new_tag)
            tags.append(new_tag)
            request.session["tags"] = tag_list

        elif request.POST.get('save') and new_proj.is_valid() and new_req.is_valid():
            code_request              = new_req.save()
            project                   = new_proj.save(commit=False)
            project.owner             = Person.objects.get(user=request.user) # Set creator
            project.code_request      = code_request
            project.save()

            for doc in docs:
                project.docs.add(doc)
                project.save()
            
            for tag in tags:
                project_tag = None
                try:
                    # Trying get an existing tag
                    project_tag = ProjectTag.objects.get( name = tag.name ) 
                except:
                    # Otherwise you need to create a new tag
                    tag.save()
                    project_tag = tag
            
                # Save the tag in the project (existing or new)
                project.tags.add( project_tag )
                project.save()

            return HttpResponseRedirect( settings.CODEMATCH_PREFIX + '/codematch/requests/'+str(project.id) )
        
        request.session['project_instance'] = new_proj
        request.session['request_instance'] = new_req
        
        proj_form = new_proj
        req_form  = new_req

    return render_page(request, template, {
        'projectcontainer' : project_container,
        'projform'         : proj_form,
        'reqform'          : req_form,
        'docform'          : doc_form,
        'tagform'          : tag_form,
        'docs'             : docs,
        'tags'             : tags,
        'myrequest'        : is_my_request
    })
    

@login_required(login_url = settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def update(request, pk):
    """ Update CodeRequest Entry """
    
    project_container = get_object_or_404(ProjectContainer, id=pk)
    
    #(TODO: Centralize this?)
    user = Person.objects.get( user = request.user )
    
    # Project must have been created by the current user
    if project_container.owner != user:
        raise Http404
    
    # User must have permission to add new CodeRequest
    if not is_user_allowed(request.user, "caneditrequest"):
        raise Http404
    
    request.session['project_instance'] = ProjectContainerForm(instance=project_container)
    request.session['request_instance'] = CodeRequestForm(instance=project_container.code_request)
    
    return save_project(request, 'codematch/requests/edit.html', project_container)

@login_required(login_url = settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def new(request):
    """ New CodeRequest Entry """
    
	# User must have permission to add new CodeRequest
    if not is_user_allowed(request.user, "canaddrequest"):
        raise Http404

    return save_project(request, 'codematch/requests/new.html')

