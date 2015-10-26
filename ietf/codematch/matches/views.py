import datetime

from ietf.codematch import constants

from django.shortcuts import get_object_or_404

from django import forms
from django.forms import CharField
from django.forms import ModelForm
from django.forms.models import modelform_factory, inlineformset_factory
from django.db.models import Count

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect

from django.contrib.auth.decorators import login_required

from ietf.group.models import Group
from ietf.person.models import Person
from ietf.doc.models import DocAlias, Document

from ietf.codematch.matches.forms import SearchForm, ProjectContainerForm, CodingProjectForm, LinkImplementationForm
from ietf.codematch.requests.forms import TagForm, DocNameForm
from ietf.codematch.matches.models import ProjectContainer, CodingProject, Implementation, ProjectTag
from ietf.codematch.requests.models import CodeRequest

from ietf.codematch.helpers.utils import (render_page, is_user_allowed, clear_session, get_user)

from django.core.urlresolvers import resolve

from django.conf import settings

import debug                            

def show_list(request, is_my_list="False", att=constants.ATT_CREATION_DATE, state=""):
    """ List all Codematches 
		type_list (all = All CodeRequests / mylist = CodeRequests I've Created / mentoring = CodeRequests i'm mentoring)
		att = List will be sorted by this attribute (eg. if creation_date then ordered by date)
		state = if the state is true then the project_containers has been previously loaded (eg. Loaded from the search) """
    
    user = get_user(request)
    
    all_projects = []
    
    if state == "True" and constants.ALL_PROJECTS in request.session:
        all_projects = request.session[constants.ALL_PROJECTS]
        request.session[constants.MAINTAIN_STATE] = True
    else:
        all_projects = ProjectContainer.objects.all()
    
    project_containers  = []
    codings             = CodingProject.objects.order_by(att)[:20]
    for coding in codings:
        for project in all_projects:
            if project not in project_containers and coding in project.codings.all() and (is_my_list == "False" or user == coding.coder):
                project_containers.append(project)
    
    docs = []
    
    areas_list, working_groups_list = ([] for i in range(2))
    
    for project_container in project_containers:
        areas, working_groups = ([] for i in range(2))
        # According to model areas and working groups should come from documents
        for doc in project_container.docs.all():
            group = doc.document.group
            if not group.name in working_groups:
                working_groups.append(group.name)
            if group.parent:
                if not group.parent.name in areas:
                    areas.append(group.parent.name)
            else:
                if not working_group in areas:
                    areas.append(working_group)
        if not areas:
            areas          = [constants.STRING_NONE]
        if not working_groups:
            working_groups = [constants.STRING_NONE]
            
        areas_list.append((areas, project_container))   
        working_groups_list.append((working_groups, project_container))
    
    docs = list(set(docs))
    
    return render_page(request, constants.TEMPLATE_MATCHES_LIST, {
        'projectcontainers'  : project_containers,
        'owner'              : user,
        'docs'               : docs,
        'areas_list'         : areas_list,
        'workinggroups_list' : working_groups_list,
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
            if not group.name in areas:
                areas.append(group.name)    
    
    tags += coding.tags.all()
    
    if not areas:
        areas          = [constants.STRING_NONE]
    if not tags:
        tags           = [constants.STRING_NONE]
		  
    return render_page(request, constants.TEMPLATE_MATCHES_SHOW, {
		'projectcontainer': project_container,
        'coding'          : coding,
        'areas'           : areas,
        'tags'            : tags,
        'owner'           : user
    })

def search(request, is_my_list="False"):
    """ Shows the list of CodeMatches, filtering according to the selected checkboxes """
    
    search_type = request.GET.get("submit")
    if search_type:
            
		ids = []
		
		if request.GET.get(constants.STRING_TITLE):
			ids += ProjectContainer.objects.filter(codings__title__icontains=query).values_list('id', flat=True)
						
		if request.GET.get(constants.STRING_DESCRIPTION):
			ids += ProjectContainer.objects.filter(codings__additional_information__icontains=query).values_list('id', flat=True)
			
		if request.GET.get(constants.STRING_PROTOCOL):
			ids += ProjectContainer.objects.filter(protocol__icontains=query).values_list('id', flat=True)
		
		if request.GET.get(constants.STRING_CODER):
			ids += ProjectContainer.objects.filter(codings__coder__name__icontains=query).values_list('id', flat=True)
			
		if request.GET.get(constants.STRING_AREA):
			ids += ProjectContainer.objects.filter(docs__document__group__parent__name__icontains=query).values_list('id', flat=True)
					
		if request.GET.get(constants.STRING_WORKINGGROUP):
			ids += ProjectContainer.objects.filter(docs__document__group__name__icontains=query).values_list('id', flat=True)    
		
		project_containers = ProjectContainer.objects.filter(id__in=list(set(ids)))
		
		request.session[constants.ALL_PROJECTS] = project_containers
		
		request.session[constants.MAINTAIN_STATE] = True
		
		return HttpResponseRedirect(settings.CODEMATCH_PREFIX + '/codematch/matches/show_list/' + is_my_list + '/creation_date/' +'True')

    else:
		return render_page(request, constants.TEMPLATE_MATCHES_SEARCH, { 
			"form" : SearchForm() 
		})
		
def save_code(request, template, pk, ck="", coding=None ):
    ''' Used to create or update a CodeRequest.
    When project container is null then a new 
    instance is created in the database'''
    
    # User must have permission to add new CodeRequest
    if not is_user_allowed(request.user, "canaddcode"):
        raise Http404
    
    doc_form = DocNameForm()
    link_form = LinkImplementationForm()
    tag_form  = modelform_factory(ProjectTag, form=TagForm)
    
    user = get_user(request)
    
	# TODO: check permission
    can_add_documents = is_user_allowed(user, "canadddocuments")    
    can_add_links = is_user_allowed(user, "canaddlinks")
    can_add_tags  = is_user_allowed(user, "canaddtags")
    
    project_container = None
    if constants.ACTUAL_PROJECT in request.session:
        project_container = request.session[constants.ACTUAL_PROJECT]
    
    # If not there in the current session then should be setted a default
    proj_form = request.session[constants.PROJECT_INSTANCE] if constants.PROJECT_INSTANCE in request.session else ProjectContainerForm()
    code_form = request.session[constants.CODE_INSTANCE] if constants.CODE_INSTANCE in request.session else CodingProjectForm()
    
    docs  = request.session[constants.ADD_DOCS]
    links = request.session[constants.ADD_LINKS]
    tags  = request.session[constants.ADD_TAGS]
    
    previous_template = "codematch/matches/show_list" # Fix this
	
    if constants.PREVIOUS_TEMPLATE not in request.session:
        request.session[constants.PREVIOUS_TEMPLATE] = previous_template
    
    if request.method == 'POST':
        
        implementation = LinkImplementationForm(request.POST)
        tag            = TagForm(request.POST)
        doc_name       = request.POST.get("doc")
        
        project = None
        new_project = None
        # If there wasn't associated Project Container, must create a new one. Functionality used to legacy RFC.
        if project_container == None:
            post = request.POST.copy()
            post._mutable = True
            post[constants.STRING_TITLE] = post.getlist(constants.STRING_TITLE)[0]  
            new_project = ProjectContainerForm(post)
            
            if new_project.is_valid():
                project = new_project.save() # Create new
                project.owner = Person.objects.get( user=request.user )
        elif project_container.code_request == None:
            post = request.POST.copy()
            post._mutable = True
            post[constants.STRING_TITLE] = post.getlist(constants.STRING_TITLE)[0]  
            new_project = ProjectContainerForm(post, instance=project_container)
            if new_project.is_valid():
                project = new_project.save()
        else:
            project = project_container # Update only
          
        if coding != None:
            new_code = CodingProjectForm(request.POST, instance=coding)
        else:
            new_code = CodingProjectForm(request.POST)

        # Adding document to the documents list to be saved in the project
        if request.POST.get(constants.STRING_LINK) and implementation.is_valid():
            new_link = implementation.save(commit=False)
            links.append(new_link)  # Updating tags to appear after rendering
            
        # Adding document to the documents list to be saved in the project
        elif doc_name:
            selected_document = DocAlias.objects.filter(name=doc_name)
            if selected_document:
                new_doc = selected_document[0]
                docs.append(new_doc)  # Updating documents to appear after rendering
            
        # Adding new tag to the tags list to be saved in the project
        elif request.POST.get(constants.STRING_TAG) and tag.is_valid():
            new_tag = tag.save(commit=False)
            new_tag.name = "#" + new_tag.name
            tags.append(new_tag)  # Updating tags to appear after rendering
        
        # Saving project (new or not) in the database
        elif request.POST.get(constants.STRING_SAVE) and project != None and new_code.is_valid():
        
            coding_project       = new_code.save(commit=False)
            coding_project.coder = Person.objects.get( user=request.user )
            coding_project.save()
            project.codings.add(coding_project)
            project.save()
            
            modified = False
            
            rem_docs = request.session[constants.REM_DOCS]
            rem_links = request.session[constants.REM_LINKS]
            rem_tags = request.session[constants.REM_TAGS]
            
            for link in rem_links:
                coding_project.links.remove(link)
                modified = True
                
            for tag in rem_tags:
                coding_project.tags.remove(tags)
                modified = True
                
            for doc in rem_docs:
                project.docs.remove(doc)
                modified = True
            
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
                modified = True   
            
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
                modified = True    
            
            for doc in docs:
                project.docs.add(doc)
                modified = True 
            
            if modified:
                coding_project.save()
                project.save()

            return HttpResponseRedirect( settings.CODEMATCH_PREFIX + "/codematch/matches/" + str(project.id) + '/' + str(coding_project.id) )
        
        # Updating session variables
        #if new_project != None and ( project_container == None or project_container.code_request != None ):
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
        'docform'          : doc_form,
        'pk'               : pk,
        'ck'               : ck,
        'links'            : links,
        'tags'             : tags,
        'docs'             : docs,
        'canadddocuments'  : can_add_documents,
        'canaddlinks'      : can_add_links,
        'canaddtags'       : can_add_tags
    })

@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def edit(request, pk, ck):
    """ Edit CodeRequest Entry """
	
    project_container = get_object_or_404(ProjectContainer, id=pk)
    coding            = get_object_or_404(CodingProject, id=ck)
    
    if request.path != request.session[constants.ACTUAL_TEMPLATE]:
        clear_session(request)
        request.session[constants.REM_LINKS] = []
        request.session[constants.REM_TAGS]  = []
        request.session[constants.REM_DOCS]  = []
    
    request.session[constants.MAINTAIN_STATE] = True
    
	# Fills session variables with project values already saved
	
    if constants.ADD_LINKS not in request.session:
        links = coding.links.all()
        request.session[constants.ADD_LINKS] = list(links)
    
    if constants.ADD_TAGS not in request.session:
        tags = coding.tags.all()
        request.session[constants.ADD_TAGS] = list(tags)
        
    if constants.ADD_DOCS not in request.session:
        docs = project_container.docs.all()
        request.session[constants.ADD_DOCS] = list(docs)
    
    # TODO: Review this        
    us = get_user(request)
    user = us
    
    # Project must have been created by the current user and
    # User must have permission to add new CodeRequest
    if coding.coder != user:
        raise Http404
     
    # Save project and code request in the cache to make 'update' and 'new' use the same code (save_project)
    if project_container.code_request == None:
        request.session[constants.PROJECT_INSTANCE] = ProjectContainerForm(instance=project_container)
    request.session[constants.ACTUAL_PROJECT] = project_container
    request.session[constants.CODE_INSTANCE]  = CodingProjectForm(instance=coding)
    
    return save_code(request, constants.TEMPLATE_MATCHES_EDIT, pk, ck, coding )

@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def new(request, pk=""):
    ''' New CodeMatch Entry
    When user presses 'Associate new project' there is a Project Container
    associated, then you need reuse this information in the form '''
    
    if request.path != request.session[constants.ACTUAL_TEMPLATE]:
        clear_session(request)
        request.session[constants.REM_LINKS] = []
        request.session[constants.REM_TAGS]  = []
        request.session[constants.REM_DOCS]  = []
        request.session[constants.ADD_LINKS] = []
        request.session[constants.ADD_TAGS]  = []
        request.session[constants.ADD_DOCS]  = []
    
    request.session[constants.MAINTAIN_STATE] = True
    
    if pk != "":
        request.session[constants.ACTUAL_PROJECT] = get_object_or_404(ProjectContainer, id=pk)
    
    # User must have permission to add new CodeMatch
    if not is_user_allowed(request.user, "canaddmatch"):
        raise Http404

    return save_code(request, constants.TEMPLATE_MATCHES_NEW, pk)
    
@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def remove_link(request, ck, link_name):
    ''' Adds the removal list, but will only be removed when saving changes
    ck (ck = 0 - new CodeMatch / ck > 0 edit CodeMatch '''
    
    refresh_template = request.session[constants.ACTUAL_TEMPLATE]
    
    links = request.session[constants.ADD_LINKS]  
    link = next(el for el in links if el.link == link_name)
    if ck != "0":
        coding = get_object_or_404(CodingProject, id=ck)
    
        # TODO: Review this        
        us = get_user(request)
        user = us
    
        # Coding must have been created by the current user and
        if coding.coder != user:
            raise Http404
    
        if coding.links.filter(link=link_name):
            cache_list = request.session[constants.REM_LINKS]
            cache_list.append(link)
    
    links.remove(link)
    request.session[constants.ADD_LINKS] = links
    
    # TODO: Centralize this?
    return HttpResponseRedirect(refresh_template)
    
@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def remove_tag(request, ck, tag_name):
    ''' Adds the removal list, but will only be removed when saving changes
    	ck (ck = 0 - new CodeMatch / ck > 0 edit CodeMatch '''
    
    refresh_template = request.session[constants.ACTUAL_TEMPLATE]
    
    tags = request.session[constants.ADD_TAGS]
    tag = next(el for el in tags if el.name == tag_name)
    
    if ck != "0":
        coding = get_object_or_404(CodingProject, id=ck)

        # TODO: Review this        
        us = get_user(request)
        user = us

        # Coding must have been created by the current user and
        if coding.coder != user:
            raise Http404
    
        if coding.tags.filter(name=tag_name):
            cache_list = request.session[constants.REM_TAGS]
            cache_list.append(tag)
    
    tags.remove(tag)
    request.session[constants.ADD_TAGS] = tags
    
    # TODO: Centralize this?
    return HttpResponseRedirect(refresh_template)

@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def remove_document(request, pk, doc_name):
    ''' Adds the removal list, but will only be removed when saving changes
        pk (pk = 0 - new ProjectContainer / pk > 0 - edit ProjectContainer '''
    
    refresh_template = request.session[constants.ACTUAL_TEMPLATE]
    
    docs = request.session[constants.ADD_DOCS]
    document = next(el for el in docs if el.name == doc_name)
    
    if pk != "0":
        project_container = get_object_or_404(ProjectContainer, id=pk)
        
        # TODO: Review this        
        us = get_user(request)
        user = us
        
        # Project must have been created by the current user and
        if project_container.owner != user:
            raise Http404
        
        if project_container.docs.filter(name=doc_name):
            cache_list = request.session[constants.REM_DOCS]
            cache_list.append(document)
            
    docs.remove(document)
    request.session[constants.ADD_DOCS] = docs
    
    # TODO: Centralize this?
    return HttpResponseRedirect(refresh_template)