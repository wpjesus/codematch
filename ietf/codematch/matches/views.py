import datetime

from ietf.codematch import constants

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
from ietf.codematch.requests.forms import TagForm
from ietf.codematch.matches.models import ProjectContainer, CodingProject, Implementation, ProjectTag
from ietf.codematch.requests.models import CodeRequest

from ietf.codematch.helpers.utils import (render_page, is_user_allowed, clear_session, get_user)

from django.core.urlresolvers import resolve

from django.conf import settings

import debug                            

def show_list(request, is_my_list="False", att="creation_date", state=""):
    """ List all ProjectContaineres by Title """
    
    user = get_user(request)
    
    all_projects = []
    
    if state == "True" and constants.ALL_PROJECTS in request.session:
        all_projects = request.session[constants.ALL_PROJECTS]
        request.session[constants.MAINTAIN_STATE] = True
    else:
        all_projects = ProjectContainer.objects.all()
    
    # Centralize this?
    project_containers  = []
    codings             = CodingProject.objects.order_by(att)[:20]
    for coding in codings:
        for project in all_projects:
            if project not in project_containers and coding in project.codings.all() and (is_my_list == "False" or user == coding.coder):
                project_containers.append(project)
    
    docs = []
    
    for project in project_containers:
        for doc in project.docs.all():
            docs.append(doc)
        
    docs = list(set(docs))
    
    return render_page(request, constants.TEMPLATE_MATCHES_LIST, {
        'projectcontainers'  : project_containers,
        'owner'              : user,
        'docs'               : docs,
        'attribute'          : att,
        'mylist'             : is_my_list,
        'state'              : state,
        'template'           : 'ietf.codematch.matches.views.show_list' # TODO fix this
    })

def show(request, pk, ck):
    """ Show individual Codematch Project and Add Implementation """
    
    project_container = get_object_or_404(ProjectContainer, id=pk)
    coding            = get_object_or_404(CodingProject,    id=ck)
    
    areas, tags = ([] for i in range(2))
    
    user = get_user(request)
    
    # According to model areas and working groups should come from documents
    for doc in project_container.docs.all():
        group = doc.document.group
        if group.parent:
            if not group.parent.name in areas:
                areas.append(group.parent.name) # use acronym?
        else:
            areas.append(group.name) 
    
    tags += coding.tags.all()
    
    if not areas:
        areas          = ["None"]
    if not tags:
        tags           = ["None"]
    
	# TODO: Migrate to 'new'
    if request.method == 'POST':
       link_to_implementation = LinkImplementationForm(request.POST)
      
	   # Adding new implementation (Review this attribute name)
       if link_to_implementation.is_valid():
          link = link_to_implementation.save()
          
          coding.links.add(link)
          coding.save()
          return HttpResponseRedirect( settings.CODEMATCH_PREFIX + '/codematch/matches/' + str(pk) + '/' + str(ck) )
		  
    return render_page(request, constants.TEMPLATE_MATCHES_SHOW, {
		'projectcontainer': project_container,
        'coding'          : coding,
        'areas'           : areas,
        'tags'            : tags,
        'owner'           : user
    })

def search(request, is_my_list="False"):
    """ Shows the list of projects, filtering by some query (title, protocol, coder or doctitle) """
    
    search_type = request.GET.get("submit")
    if search_type:
        form = SearchForm(request.GET)
        docs = []
        project_containers = []
        
        # get query field
        query = ''
        if request.GET.get('search'):
            query = request.GET.get('search')

        if query :
            
            ids = []
            
            if request.GET.get('title'):
                ids += ProjectContainer.objects.filter(codings__title__icontains=query).values_list('id', flat=True)
                            
            if request.GET.get('description'):
                ids += ProjectContainer.objects.filter(codings__additional_information__icontains=query).values_list('id', flat=True)
                
            if request.GET.get('protocol'):
                ids += ProjectContainer.objects.filter(protocol__icontains=query).values_list('id', flat=True)
            
            if request.GET.get('coder'):
                ids += ProjectContainer.objects.filter(codings__coder__name__icontains=query).values_list('id', flat=True)
                
            if request.GET.get('area'):
                ids += ProjectContainer.objects.filter(docs__document__group__parent__name__icontains=query).values_list('id', flat=True)
                        
            if request.GET.get('workinggroup'):
                ids += ProjectContainer.objects.filter(docs__document__group__name__icontains=query).values_list('id', flat=True)    
            
            project_containers = ProjectContainer.objects.filter(id__in=list(set(ids)))
            
            user = get_user(request)
            
            request.session[constants.ALL_PROJECTS] = project_containers
            
            request.session[constants.MAINTAIN_STATE] = True
            
            return HttpResponseRedirect(settings.CODEMATCH_PREFIX + '/codematch/matches/show_list/' + is_my_list + '/creation_date/' +'True')

        return HttpResponseRedirect(request.path)

    else:
		return render_page(request, constants.TEMPLATE_MATCHES_SEARCH, { 
			"form" : SearchForm() 
		})
		
def save_code(request, template, pk, ck="", coding=None ):
    ''' Used to create or update a CodeRequest.
    When project container is null then a new 
    instance is created in the database'''

    # NOTE: Is slow 'cause of the mentors list (?)
    
    # User must have permission to add new CodeRequest
    if not is_user_allowed(request.user, "canaddcode"):
        raise Http404
    
    link_form = LinkImplementationForm()
    tag_form  = modelform_factory(ProjectTag, form=TagForm)
    
    user = get_user(request)
    
	# TODO: check permission
    can_add_links = is_user_allowed(user, "canaddlinks")
    can_add_tags  = is_user_allowed(user, "canaddtags")
    
    project_container = None
    if constants.ACTUAL_PROJECT in request.session:
        project_container = request.session[constants.ACTUAL_PROJECT]
    
    # If not there in the current session then should be setted a default
    proj_form = request.session[constants.PROJECT_INSTANCE] if constants.PROJECT_INSTANCE in request.session else ProjectContainerForm()
    code_form = request.session[constants.CODE_INSTANCE] if constants.CODE_INSTANCE in request.session else CodingProjectForm()
    
    links = request.session[constants.ADD_LINKS]
    tags  = request.session[constants.ADD_TAGS]
    
    previous_template = "codematch/matches/show_list" # Fix this
	
    if constants.PREVIOUS_TEMPLATE not in request.session:
        request.session[constants.PREVIOUS_TEMPLATE] = previous_template
    
    if request.method == 'POST':
        
        implementation = LinkImplementationForm(request.POST)
        tag            = TagForm(request.POST)
        
        project = None
        new_project = None
        # If there wasn't associated Project Container, must create a new one. Functionality used to legacy RFC.
        if project_container == None:
            new_project = ProjectContainerForm(request.POST) 
            if new_project.is_valid():
                project = new_project.save() # Create new
                project.owner = Person.objects.get( user=request.user )
        else:
            project = project_container # Update only
            
        if coding != None:
            new_code = CodingProjectForm(request.POST, instance=coding)
        else:
            new_code = CodingProjectForm(request.POST)

        # Adding document to the documents list to be saved in the project
        if request.POST.get('link') and implementation.is_valid():
            new_link = implementation.save(commit=False)
            links.append(new_link)  # Updating tags to appear after rendering
            
        # Adding new tag to the tags list to be saved in the project
        elif request.POST.get('tag') and tag.is_valid():
            new_tag = tag.save(commit=False)
            tags.append(new_tag)  # Updating tags to appear after rendering
        
        # Saving project (new or not) in the database
        elif request.POST.get('save') and project != None and new_code.is_valid():
        
            coding_project       = new_code.save(commit=False)
            coding_project.coder = Person.objects.get( user=request.user )
            coding_project.save()
            project.codings.add(coding_project)
            project.save()
            
            modify = False
            
            rem_links = request.session[constants.REM_LINKS]
            rem_tags = request.session[constants.REM_TAGS]
            
            for link in rem_links:
                coding_project.links.remove(link)
                modify = True
                
            for tag in rem_tags:
                coding_project.tags.remove(tags)
                modify = True
            
            for link in links:
                try:
                    # Trying get an existing tag
                    new_link = Implementation.objects.get(link=link.link) 
                except:
                    # Otherwise you need to create a new tag
                    link.save()
                    new_link = link
            
                # Save the tag in the project (existing or new)
                coding_project.links.add(new_link)        
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
                coding_project.tags.add(new_tag)        
                modify = True    
            
            if modify:
                coding_project.save()

            return HttpResponseRedirect( settings.CODEMATCH_PREFIX + "/codematch/matches/" + str(project.id) + '/' + str(coding_project.id) )
			
        # Updating session variables
        if new_project != None:
            request.session[constants.PROJECT_INSTANCE] = new_project
            proj_form = new_project
            
        request.session[constants.CODE_INSTANCE] = new_code
        code_form = new_code
    
    return render_page(request, template, {
        'projectcontainer' : project_container,
        'projform'         : proj_form,
        'codeform'         : code_form,
        'linkform'         : link_form,
        'tagform'          : tag_form,
        'pk'               : pk,
        'ck'               : ck,
        'links'            : links,
        'tags'             : tags,
        'canaddlinks'      : can_add_links,
        'canaddtags'       : can_add_tags
    })

@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def edit(request, pk, ck):
    """ Edit CodeRequest Entry """
    
    #template = 'codematch/matches/edit.html'
	
    project_container = get_object_or_404(ProjectContainer, id=pk)
    coding            = get_object_or_404(CodingProject, id=ck)
    
    if request.path != request.session[constants.ACTUAL_TEMPLATE]:
        clear_session(request)
        request.session[constants.REM_LINKS] = []
        request.session[constants.REM_TAGS]  = []
    
    request.session[constants.MAINTAIN_STATE] = True
    
    if constants.ADD_LINKS not in request.session:
        links = coding.links.all()
        request.session[constants.ADD_LINKS] = list(links)
    
    if constants.ADD_TAGS not in request.session:
        tags = coding.tags.all()
        request.session[constants.ADD_TAGS] = list(tags)
    
	user = get_user(request)
    
    # Project must have been created by the current user and
    # User must have permission to add new CodeRequest
    if coding.coder != user or not is_user_allowed(request.user, "caneditmatch"):
        raise Http404
     
    # Save project and code request in the cache to make 'update' and 'new' use the same code (save_project)
    request.session[constants.ACTUAL_PROJECT] = project_container
    request.session[constants.CODE_INSTANCE]  = CodingProjectForm(instance=coding)
    
    return save_code(request, constants.TEMPLATE_MATCHES_EDIT, pk, ck, coding )

@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def new(request, pk=""):
    ''' New CodeMatch Entry
    When user presses 'Associate new project' there is a Project Container
    associated, then you need reuse this information in the form '''
    
    #template = 'codematch/matches/new.html'
    
    if request.path != request.session[constants.ACTUAL_TEMPLATE]:
        clear_session(request)
        request.session[constants.REM_LINKS] = []
        request.session[constants.REM_TAGS]  = []
        request.session[constants.ADD_LINKS] = []
        request.session[constants.ADD_TAGS]  = []
    
    request.session[constants.MAINTAIN_STATE] = True
    
    if pk != "":
        request.session[constants.ACTUAL_PROJECT] = get_object_or_404(ProjectContainer, id=pk)
    
    # User must have permission to add new CodeMatch
    if not is_user_allowed(request.user, "canaddmatch"):
        raise Http404

    return save_code(request, constants.TEMPLATE_MATCHES_NEW, pk)
    
@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def remove_link(request, ck, link_name):
    
    refresh_template = request.session[constants.ACTUAL_TEMPLATE]
    
    links = request.session[constants.ADD_LINKS]  
    link = next(el for el in links if el.link == link_name)
    
    if ck != "0":
        coding = get_object_or_404(CodingProject, id=ck)
    
        if coding.links.filter(link=link_name):
            cache_list = request.session[constants.REM_LINKS]
            cache_list.append(link)
    
    links.remove(link)
    request.session[constants.ADD_LINKS] = links
    
    # TODO: Centralize this?
    return HttpResponseRedirect(request.path)
    
@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def remove_tag(request, ck, tag_name):
    
    refresh_template = request.session[constants.ACTUAL_TEMPLATE]
    
    tags = request.session[constants.ADD_TAGS]
    tag = next(el for el in tags if el.name == tag_name)
    
    if ck != "0":
        coding = get_object_or_404(CodingProject, id=ck)
    
        if coding.tags.filter(name=tag_name):
            cache_list = request.session[constants.REM_TAGS]
            cache_list.append(tag)
    
    
    tags.remove(tag)
    request.session[constants.ADD_TAGS] = tags
    
    return HttpResponseRedirect(request.path)