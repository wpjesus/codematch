import datetime

from ietf.codematch import constants

from django.shortcuts import get_object_or_404

from django import forms
from django.forms.models import modelform_factory
from django.db.models import Count

from django.http import Http404, HttpResponseRedirect

from django.contrib.auth.decorators import login_required

from ietf.group.models import Group
from ietf.person.models import Person
from ietf.doc.models import DocAlias, Document

from ietf.codematch.matches.forms import SearchForm, ProjectContainerForm, MailForm
from ietf.codematch.requests.forms import CodeRequestForm, DocNameForm, TagForm

from ietf.codematch.matches.models import ProjectContainer, CodingProject, ProjectTag, ProjectMail
from ietf.codematch.requests.models import CodeRequest

from ietf.codematch.helpers.utils import (render_page, is_user_allowed, clear_session, get_user)

from django.core.urlresolvers import resolve

from django.conf import settings

import debug                            

def show_list(request, type_list="all", att="creation_date", state=""):
    """ List all CodeRequests """
    
    user = get_user(request)
    
    if state == "True" and constants.ALL_PROJECTS in request.session:
        project_containers = request.session[constants.ALL_PROJECTS]
        request.session[constants.MAINTAIN_STATE] = True
    else:
        if type_list == "mylist":
            # Project must have been created by the current user and user must have permission mentor
            if not is_user_allowed(user, "iscreator"):
                raise Http404
            project_containers = ProjectContainer.objects.exclude(code_request__isnull=True).filter(owner=user)
        elif type_list == "mentoring":
            # Project must have been mentored by the current user and user must have permission mentor
            if not is_user_allowed(user, "ismentor"):
                raise Http404
            project_containers = ProjectContainer.objects.exclude(code_request__isnull=True).filter(code_request__mentor=user)
        else:
            # TODO: Allow sorting by different parameters (for others templates too)
            # Exclude ProjectContainers that don't have an associated CodeRequest (TODO: Centralize this?)
            project_containers = ProjectContainer.objects.exclude(code_request__isnull=True)
    
    if att == 'popularity': # TODO: Fix this
        project_containers = project_containers.annotate(count=Count('codings')).order_by('-count')[:20]
    else:
        project_containers = project_containers.order_by(att)[:20]
            
    list_of_lists = []
    
    dict = {'protocol':'protocol', 'docs__document__group__name':'working_group', 'docs__document__group__parent__name':'area'}
    
    if att in dict:
        select = list(set(project_containers.values_list(att, flat=True)))
        print select
        for s in select:
            newlist = []
            val = dict[att]
            for p in project_containers:
                if att == 'protocol':
                    prop = getattr(p, val)
                else:
                    prop = None
                    for d in p.docs.all():
                        if val == 'working_group':
                            prop = d.document.group.name
                        else:
                            prop = d.document.group.parent.name
                if prop != None and p not in newlist and prop == s:
                    newlist.append(p)
            if len(newlist) > 0:
                list_of_lists.append((newlist,s))
    else:
        for p in project_containers:
            newlist = []
            newlist.append(p)
            list_of_lists.append((newlist,""))
    
    return render_page(request, constants.TEMPLATE_REQUESTS_LIST, {
		'projectcontainers' : list_of_lists,
        'owner'             : user,
        'attribute'         : att,
        'typelist'          : type_list,
        'state'             : state,
        'template'          : 'ietf.codematch.requests.views.show_list'
    }) 

def search(request, type_list="all"):
    """ Shows the list of projects, filtering by some query (title, protocol or mentor) """
    
    search_type = request.GET.get("submit")
    if search_type:
    
        # get query field
        query = ''
        if request.GET.get(search_type):
            query = request.GET.get(search_type)
        
        if query:
                    
            user = None
            ids = []
            
            # TODO: Localize strings
            if request.GET.get('title'):
                ids += ProjectContainer.objects.filter(title__icontains=query).values_list('id', flat=True)
           
            if request.GET.get('description'):
                ids += ProjectContainer.objects.filter(description__icontains=query).values_list('id', flat=True)
                
            if request.GET.get('protocol'):
                ids += ProjectContainer.objects.filter(protocol__icontains=query).values_list('id', flat=True)
            
            if request.GET.get('mentor'):
                ids += ProjectContainer.objects.filter(code_request__mentor__name__icontains=query).values_list('id', flat=True)
                        
            if request.GET.get('docs'):
                ids += ProjectContainer.objects.filter(docs__name__icontains=query).values_list('id', flat=True)
                        
            if request.GET.get('area'):
                ids += ProjectContainer.objects.filter(docs__document__group__parent__name__icontains=query).values_list('id', flat=True)
                        
            if request.GET.get('workinggroup'):
                ids += ProjectContainer.objects.filter(docs__document__group__name__icontains=query).values_list('id', flat=True)         
                        
            project_containers = ProjectContainer.objects.filter(id__in=list(set(ids)))
                        
            user = get_user(request)
            
            request.session[constants.ALL_PROJECTS] = project_containers
            
            request.session[constants.MAINTAIN_STATE] = True
            
            return HttpResponseRedirect(settings.CODEMATCH_PREFIX + '/codematch/requests/show_list/' + type_list + '/creation_date/' +'True')
            
        else:
            return HttpResponseRedirect(request.path)
    
    else:
        return render_page(request, constants.TEMPLATE_REQUESTS_SEARCH, {
			"form" : SearchForm() 
        })

def show(request, pk):
    """ Show individual Codematch Project """
    
    project_container = get_object_or_404(ProjectContainer, id=pk)
    
    areas, working_groups, tags = ([] for i in range(3))
    
    user = get_user(request)
	
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
    
    if not areas:
        areas = ["None"]
    if not working_groups:
        working_groups = ["None"]

    return render_page(request, constants.TEMPLATE_REQUESTS_SHOW, {
		'projectcontainer': project_container,
        'areas'           : areas,
        'workinggroups'   : working_groups,
        'owner'           : user
    })

def save_project(request, template, project_container=None):
    ''' Used to create or update a CodeRequest.
    When project container is null then a new 
    instance is created in the database'''

    # NOTE: Is slow 'cause of the mentors list (?)
	
    user = get_user(request)
    
    doc_form = DocNameForm()
    tag_form = modelform_factory(ProjectTag, form=TagForm)
    
	# TODO: check permission
    can_add_documents = is_user_allowed(user, "canadddocuments")
    can_add_tags      = is_user_allowed(user, "canaddtags")
    can_add_mail      = is_user_allowed(user, "canaddmail")
    
	# If not there in the current session then should be setted a default
    proj_form = request.session[constants.PROJECT_INSTANCE] if constants.PROJECT_INSTANCE in request.session else ProjectContainerForm()
    req_form = request.session[constants.REQUEST_INSTANCE] if constants.REQUEST_INSTANCE in request.session else CodeRequestForm()
    mail_form = request.session[constants.MAIL_INSTANCE] if constants.MAIL_INSTANCE in request.session else MailForm()
    
    docs  = request.session[constants.ADD_DOCS]
    tags  = request.session[constants.ADD_TAGS]
    mails = request.session[constants.ADD_MAILS]
    
    previous_template = "codematch/requests/show_list"
    
    if constants.PREVIOUS_TEMPLATE not in request.session:
        request.session[constants.PREVIOUS_TEMPLATE] = previous_template
    
    if request.method == 'POST':
        
        doc_name = request.POST.get("doc")
        tag = TagForm(request.POST)
        new_mail = MailForm(request.POST)
        
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
            
        # Adding new mail to the mailing list to be saved in the project
        elif new_mail.is_valid():
            m = new_mail.save(commit=False)
            if m.type == 'Twitter': # TODO: Padronize for this and others
                m.mail = '@' + m.mail 
            mails.append(m)
		
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
            
            for mail in mails:
                try:
                    new_m = ProjectMail.objects.get(mail=mail.mail, type=mail.type)
                except:
                    mail.save()
                    new_m = mail
                    
                project.mails.add(new_m)
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
        'mailform'         : mail_form,
        'docform'          : doc_form,
        'tagform'          : tag_form,
        'docs'             : docs,
        'tags'             : tags,
        'mails'            : mails,
        'canadddocuments'  : can_add_documents,
        'canaddtags'       : can_add_tags,
        'canaddmail'       : can_add_mail
    })

@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def edit(request, pk):
    """ Edit CodeRequest Entry """
    
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
        
    if constants.ADD_MAILS not in request.session:
        mails = project_container.mails.all()
        request.session[constants.ADD_MAILS] = list(mails)
        
    user = get_user(request)
    # Project must have been created by the current user and
	# User must have permission to add new CodeRequest
    #if project_container.owner != user or is_user_allowed(user, "caneditrequest"):
    #    raise Http404
    
	# Save project and code request in the cache to make 'update' and 'new' use the same code (save_project)
    request.session[constants.PROJECT_INSTANCE] = ProjectContainerForm(instance=project_container)
    request.session[constants.REQUEST_INSTANCE] = CodeRequestForm(instance=project_container.code_request)
    
    return save_project(request, constants.TEMPLATE_REQUESTS_EDIT, project_container)

@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def new(request):
    """ New CodeRequest Entry """
    
    if request.path != request.session[constants.ACTUAL_TEMPLATE]:
        clear_session(request)
        request.session[constants.REM_DOCS] = []
        request.session[constants.REM_TAGS] = []
        request.session[constants.ADD_MAILS] = []
        request.session[constants.ADD_DOCS] = []
        request.session[constants.ADD_TAGS] = []
    
    request.session[constants.MAINTAIN_STATE] = True

    return save_project(request, constants.TEMPLATE_REQUESTS_NEW)

@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
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
        
    return HttpResponseRedirect(refresh_template)
    
@login_required(login_url = settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
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
        
    return HttpResponseRedirect(refresh_template)

