import datetime

from ietf.codematch import constants

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

from ietf.codematch.helpers.utils import (render_page, is_user_allowed, clear_session)

from django.conf import settings

import debug                            

def show_list(request): 
    """ List all CodeRequests """
    
    # TODO: Allow sorting by different parameters (for others templates too)
    # Exclude ProjectContainers that don't have an associated CodeRequest (TODO: Centralize this?)
    project_containers = ProjectContainer.objects.exclude(code_request__isnull=True).order_by('creation_date')[:20]
    
    user = None
    
    if request.user.is_authenticated():
        # (TODO: Centralize this?)
        user = Person.objects.get(user=request.user)
    
    return render_page(request, "codematch/requests/list.html", {
            'projectcontainers' : project_containers,
            'owner'             : user
    }) 

@login_required(login_url=settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def show_my_list(request):
    """ List CodeRequests i've created """
    
    # (TODO: Centralize this?)
    user = Person.objects.get(user=request.user)
    
    # Exclude ProjectContainers that don't have an associated CodeRequest (TODO: Centralize this?)
    project_containers = ProjectContainer.objects.exclude(code_request__isnull=True).filter(owner=user).order_by('creation_date')[:20]
    
	# Project must have been created by the current user and user must have permission mentor
    if not is_user_allowed(user, "iscreator") and project_containers.count() == 0:
        raise Http404
    
    return render_page(request, "codematch/requests/list.html", {
            'projectcontainers' : project_containers,
            'owner'             : user
    })

@login_required(login_url=settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def show_mentoring_list(request):
    """ List CodeRequests i'm mentoring """
    
    # (TODO: Centralize this?)
    user = Person.objects.get(user=request.user)
    
    # Exclude ProjectContainers that don't have an associated CodeRequest (TODO: Centralize this?)
    project_containers = ProjectContainer.objects.exclude(code_request__isnull=True).filter(code_request__mentor=user).order_by('creation_date')[:20]
    
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
                    
            user = None
    
            if request.user.is_authenticated():
                # (TODO: Centralize this?)
                user = Person.objects.get(user=request.user)
            
            if search_type == "title":
                project_containers = ProjectContainer.objects.filter(title__icontains=query) | ProjectContainer.objects.filter(description__icontains=query) 
            
            elif search_type == "protocol":
                project_containers = ProjectContainer.objects.filter(protocol__icontains=query) 
            
            elif search_type == "mentor":
                project_containers = ProjectContainer.objects.filter(code_request__mentor__name__icontains=query) 
            
            else:
                raise Http404("Unexpected search type in ProjectContainer query: %s" % search_type)
            
            return render_page(request, "codematch/requests/list.html", {
                "projectcontainers" : project_containers,
                'owner'             : user
            })
            
        else:
            return HttpResponseRedirect(request.path)
    
    else:
        form = SearchForm()
        return render_page(request, "codematch/requests/search.html", { 
            "form" : form 
        })

def show(request, pk):
    """ Show individual Codematch Project """
    
    project_container = get_object_or_404(ProjectContainer, id=pk)
    
    areas, working_groups, tags = ([] for i in range(3))
    
    user = None
    
    if request.user.is_authenticated():
        # (TODO: Centralize this?)
        user = Person.objects.get(user=request.user)
	
    # According to model areas and working groups should come from documents
    for doc in project_container.docs.all():
        group = doc.document.group
        if not group.name in working_groups:
            working_groups.append(group.name)
        if group.parent:
            if not group.parent.name in areas:
                areas.append(group.parent.name)  # use acronym?
        else:
            areas.append(working_group) 
    
    tags += project_container.tags.all()
    
    if not areas:
        areas = ["None"]
    if not working_groups:
        working_groups = ["None"]
    if not tags:
        tags = ["None"]
    
    return render_page(request, "codematch/requests/show.html", {
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
    
    doc_form = DocNameForm()
    tag_form = modelform_factory(ProjectTag, form=TagForm)
    
    # (TODO: Centralize this?)
    user = Person.objects.get(user=request.user)
    # TODO: check permission
    can_add_documents = is_user_allowed(user, "canadddocuments")
    can_add_tags      = is_user_allowed(user, "canaddtags")
    
	# If not there in the current session then should be setted a default
    proj_form = request.session[constants.PROJECT_INSTANCE] if constants.PROJECT_INSTANCE in request.session else ProjectContainerForm()
    req_form = request.session[constants.REQUEST_INSTANCE] if constants.REQUEST_INSTANCE in request.session else CodeRequestForm()
    
    docs = request.session[constants.ADD_DOCS]
    tags = request.session[constants.ADD_TAGS]
    
    previous_template = "codematch/requests/show_list"
    
    if constants.PREVIOUS_TEMPLATE not in request.session:
        request.session[constants.PREVIOUS_TEMPLATE] = previous_template
    
    if request.method == 'POST':
        
        doc_name = request.POST.get("doc")
        tag = TagForm(request.POST)
        
        if project_container != None:
            new_proj = ProjectContainerForm(request.POST, instance=project_container)
            new_req = CodeRequestForm(request.POST, instance=project_container.code_request)
        else:
            new_proj = ProjectContainerForm(request.POST)
            new_req = CodeRequestForm(request.POST)

        # Adding document to the documents list to be saved in the project
        if doc_name:
            selected_document = DocAlias.objects.filter(name=doc_name)
            if selected_document:
                new_doc = selected_document[0]
                docs.append(new_doc)  # Updating documents to appear after rendering
            
        # Adding new tag to the tags list to be saved in the project
        elif tag.is_valid():
            new_tag = tag.save(commit=False)
            tags.append(new_tag)  # Updating tags to appear after rendering
		
		# Saving project (new or not) in the database
        elif request.POST.get('save') and new_proj.is_valid() and new_req.is_valid():
			# Creating new (or update) instance of the code request in the database
            code_request = new_req.save()
			# Creating new (or update) instance of the project container in the database
            project = new_proj.save(commit=False)
            project.owner = Person.objects.get(user=request.user)  # Set creator
            project.code_request = code_request  # Linking CodeRequest to Project
            project.save()
            
            modify = False
            
            rem_docs = request.session[constants.REM_DOCS]
            rem_tags = request.session[constants.REM_TAGS]
            
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
                    new_tag = ProjectTag.objects.get(name=tag.name) 
                except:
                    # Otherwise you need to create a new tag
                    tag.save()
                    new_tag = tag
            
                # Save the tag in the project (existing or new)
                project.tags.add(new_tag)		
                modify = True	
            
            if modify:
                project.save()

            return HttpResponseRedirect(settings.CODEMATCH_PREFIX + '/codematch/requests/' + str(project.id))
        
		# Updating session variables
        request.session[constants.PROJECT_INSTANCE] = new_proj
        request.session[constants.REQUEST_INSTANCE] = new_req
        
        proj_form = new_proj
        req_form = new_req
    
    return render_page(request, template, {
        'projectcontainer' : project_container,
        'projform'         : proj_form,
        'reqform'          : req_form,
        'docform'          : doc_form,
        'tagform'          : tag_form,
        'docs'             : docs,
        'tags'             : tags,
        'canadddocuments'  : can_add_documents,
        'canaddtags'       : can_add_tags
    })

@login_required(login_url=settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def edit(request, pk):
    """ Edit CodeRequest Entry """
    
    template = 'codematch/requests/edit.html'
    
    project_container = get_object_or_404(ProjectContainer, id=pk)
    
    if request.path != request.session[constants.ACTUAL_TEMPLATE]:
        clear_session(request)
        request.session[constants.REM_DOCS] = []
        request.session[constants.REM_TAGS] = []
    
    request.session[constants.MAINTAIN_STATE] = True
    
    if constants.ADD_DOCS not in request.session:
        docs = project_container.docs.all()
        request.session[constants.ADD_DOCS] = list(docs)
    
    if constants.ADD_TAGS not in request.session:
        tags = project_container.tags.all()
        request.session[constants.ADD_TAGS] = list(tags)
    
    # (TODO: Centralize this?)
    user = Person.objects.get(user=request.user)
	
    # Project must have been created by the current user and
	# User must have permission to add new CodeRequest
    if project_container.owner != user or not is_user_allowed(request.user, "caneditrequest"):
        raise Http404
    
	# Save project and code request in the cache to make 'update' and 'new' use the same code (save_project)
    request.session[constants.PROJECT_INSTANCE] = ProjectContainerForm(instance=project_container)
    request.session[constants.REQUEST_INSTANCE] = CodeRequestForm(instance=project_container.code_request)
    
    return save_project(request, template, project_container)

@login_required(login_url=settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def new(request):
    """ New CodeRequest Entry """
    
    template = 'codematch/requests/new.html'
    
    if request.path != request.session[constants.ACTUAL_TEMPLATE]:
        clear_session(request)
        request.session[constants.REM_DOCS] = []
        request.session[constants.REM_TAGS] = []
        request.session[constants.ADD_DOCS] = []
        request.session[constants.ADD_TAGS] = []
    
    request.session[constants.MAINTAIN_STATE] = True
    
	# User must have permission to add new CodeRequest
    if not is_user_allowed(request.user, "canaddrequest"):
        raise Http404

    return save_project(request, 'codematch/requests/new.html')

@login_required(login_url=settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def remove_document(request, pk, doc_name):
    
    refresh_template = request.session[constants.ACTUAL_TEMPLATE]
    
    docs = request.session[constants.ADD_DOCS]
    document = next(el for el in docs if el.name == doc_name)
    
    if pk != "0":
        project_container = get_object_or_404(ProjectContainer, id=pk)
        
        if project_container.docs.filter(name=doc_name):
            cache_list = request.session[constants.REM_DOCS]
            cache_list.append(document)
            
    docs.remove(document)
    request.session[constants.ADD_DOCS] = docs
        
    # TODO: Centralize this?
    return HttpResponseRedirect(refresh_template)
    
@login_required(login_url=settings.CODEMATCH_PREFIX + '/codematch/accounts/login')
def remove_tag(request, pk, tag_name):
    
    refresh_template = request.session[constants.ACTUAL_TEMPLATE]
    
    tags = request.session[constants.ADD_TAGS]
    tag = next(el for el in tags if el.name == tag_name)
    
    if pk != "0":
        project_container = get_object_or_404(ProjectContainer, id=pk)
    
        if project_container.tags.filter(name=tag_name):
            cache_list = request.session[constants.REM_TAGS]
            cache_list.append(tag)
    
    tags.remove(tag)
    request.session[constants.ADD_TAGS] = tags
        
    # TODO: Centralize this?
    return HttpResponseRedirect(refresh_template)

