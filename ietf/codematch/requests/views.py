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
    
	# Project must have been created by the current user and user must have permission mentor
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
                    
            if search_type   == "title":
                project_containers  =  ProjectContainer.objects.filter(title__icontains=query) | ProjectContainer.objects.filter(description__icontains=query) 
            
            elif search_type == "protocol":
                project_containers  =  ProjectContainer.objects.filter(protocol__icontains=query) 
            
            elif search_type == "mentor":
                project_containers  = ProjectContainer.objects.filter(code_request__mentor__name__icontains=query) 
            
            else:
                raise Http404("Unexpected search type in ProjectContainer query: %s" % search_type)
            
            return render_page(request, "codematch/requests/list.html", {
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
    
    areas, working_groups, tags = ([] for i in range(3))
    
    if request.user.is_authenticated():
        #(TODO: Centralize this?)
        user = Person.objects.get( user = request.user )
	
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
    
    tags += project_container.tags.all()
    
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
        'tags'            : tags,
        'owner'           : user
    })

def save_project(request, template, project_container=None):
    ''' Used to create or update a CodeRequest.
    When project container is null then a new 
    instance is created in the database'''

    # NOTE: Is slow 'cause of the mentors list (?)
    
    # User must have permission to add new CodeRequest
    if not is_user_allowed(request.user, "canaddrequest"):
        raise Http404
    
    doc_form  = DocNameForm()
    tag_form  = modelform_factory(ProjectTag,form=TagForm)
    
    #(TODO: Centralize this?)
    user = Person.objects.get( user = request.user )
    # TODO: check permission
    is_my_request = is_user_allowed(user, "canadddocuments")
	
	# If not there in the current session then should be setted a default
    proj_form = request.session['project_instance'] if 'project_instance' in request.session else ProjectContainerForm()
    req_form  = request.session['request_instance'] if 'request_instance' in request.session else CodeRequestForm()
    
    doc_list = request.session["add_docs"]
    docs = doc_list
    tag_list = request.session["add_tags"]
    tags = tag_list
    
    previous_template = "codematch/requests/show_list"
    
    if "previous_template" not in request.session:
        request.session["previous_template"] = previous_template
    
    if request.method == 'POST':
        
        doc_name = request.POST.get("doc")
        tag      = TagForm(request.POST)
        
        if project_container != None:
            new_proj = ProjectContainerForm(request.POST, instance=project_container)
            new_req  = CodeRequestForm(request.POST, instance=project_container.code_request)
        else:
            new_proj = ProjectContainerForm(request.POST)
            new_req  = CodeRequestForm(request.POST)

        # Adding document to the documents list to be saved in the project
        if doc_name:
            selected_document = DocAlias.objects.filter( name = doc_name )
            if selected_document:
                new_doc  = selected_document[0]
                docs.append(new_doc) # Updating documents to appear after rendering
            
        # Adding new tag to the tags list to be saved in the project
        elif tag.is_valid():
            new_tag  = tag.save(commit=False)
            tags.append(new_tag) # Updating tags to appear after rendering
		
		# Saving project (new or not) in the database
        elif request.POST.get('save') and new_proj.is_valid() and new_req.is_valid():
			# Creating new (or update) instance of the code request in the database
            code_request              = new_req.save()
			# Creating new (or update) instance of the project container in the database
            project                   = new_proj.save(commit=False)
            project.owner             = Person.objects.get( user = request.user ) # Set creator
            project.code_request      = code_request # Linking CodeRequest to Project
            project.save()
            
            modify = False
            
            rem_docs = request.session["rem_docs"]
            rem_tags = request.session["rem_tags"]
            
            for doc in rem_docs:
                project.docs.remove(doc)
                modify = True
                
            for tag in rem_tags:
                project.tags.remove(tags)
                modify = True
            
            for doc in docs:
                project.docs.add(doc)
                modify = True
            
            for tag in tags:
                try:
                    # Trying get an existing tag
                    new_tag = ProjectTag.objects.get( name = tag.name ) 
                except:
                    # Otherwise you need to create a new tag
                    tag.save()
                    new_tag = tag
            
                # Save the tag in the project (existing or new)
                project.tags.add( new_tag )		
                modify = True	
            
            if modify:
                project.save()

            return HttpResponseRedirect( settings.CODEMATCH_PREFIX + '/codematch/requests/' + str(project.id) )
        
		# Updating session variables
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
    
    template = 'codematch/requests/edit.html'
    
    #TODO: Centralize this
    keys = ["project_instance", "request_instance", "add_docs", "add_tags", "rem_docs", "rem_tags"]
    
    # TODO: Centralize this
    if request.session["actual_template"] != request.path:
        for key in keys:
            if key in request.session:
                del request.session[key]
        request.session["rem_docs"] = []
        request.session["rem_tags"] = []
    
    project_container = get_object_or_404(ProjectContainer, id = pk )
    
    if "add_docs" not in request.session:
        docs = project_container.docs.all()
        request.session["add_docs"] = list(docs)
    
    if "add_tags" not in request.session:
        tags = project_container.tags.all()
        request.session["add_tags"] = list(tags)
    
    print request.session["add_docs"]
    
    #(TODO: Centralize this?)
    user = Person.objects.get( user = request.user )
	
    # Project must have been created by the current user and
	# User must have permission to add new CodeRequest
    if project_container.owner != user or not is_user_allowed(request.user, "caneditrequest"):
        raise Http404
    
	# Save project and code request in the cache to make 'update' and 'new' use the same code (save_project)
    request.session['project_instance'] = ProjectContainerForm( instance = project_container )
    request.session['request_instance'] = CodeRequestForm( instance = project_container.code_request )
    
    return save_project(request, template, project_container)

@login_required(login_url = settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def new(request):
    """ New CodeRequest Entry """
    
    template = 'codematch/requests/new.html'
    
    #TODO: Centralize this
    keys = ["project_instance", "request_instance", "add_docs", "add_tags", "rem_docs", "rem_tags"]
    
    # TODO: Centralize this
    if request.session["actual_template"] != request.path:
        for key in keys:
            if key in request.session:
                del request.session[key]
        request.session["rem_docs"] = []
        request.session["rem_tags"] = []
    
	# User must have permission to add new CodeRequest
    if not is_user_allowed(request.user, "canaddrequest"):
        raise Http404

    return save_project(request, 'codematch/requests/new.html')

@login_required(login_url = settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def remove_document(request, pk, doc_name):
    
    template = "/codematch/requests/new"
    document = None
    
    if pk != "0":
        project_container = get_object_or_404(ProjectContainer, id = pk )
        template = '/codematch/requests/update/' + str(project_container.id)
    
        selected_document = project_container.docs.filter( name = doc_name )
        if selected_document:
            document  = selected_document[0]
            cache_list = request.session["rem_docs"]
            cache_list.append(document)
            
    if document == None:
        document = get_object_or_404(DocAlias, name = doc_name )
    
    docs = request.session["add_docs"]
    docs.remove(document)
    request.session["add_docs"] = docs
        
    return HttpResponseRedirect( settings.CODEMATCH_PREFIX + template )
    
@login_required(login_url = settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def remove_tag(request, pk, tag_name):
    
    template = "/codematch/requests/new"
    tag = None
    
    if pk != "0":
        project_container = get_object_or_404(ProjectContainer, id = pk )
        template = '/codematch/requests/update/' + str(project_container.id)
    
        selected_tag = project_container.tags.filter( name = tag_name )
        if selected_tag:
            tag  = selected_document[0]
            cache_list = request.session["rem_tags"]
            cache_list.append(tag)
            
    if tag == None:
        tag = get_object_or_404(ProjectTag, name = tag_name )
    
    tags = request.session["add_tags"]
    tags.remove(tag)
    request.session["add_tags"] = tags
        
    return HttpResponseRedirect( settings.CODEMATCH_PREFIX + template )

