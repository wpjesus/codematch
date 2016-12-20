from django.shortcuts import get_object_or_404
from django.forms.models import modelform_factory
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from ietf.person.models import Person
from ietf.doc.models import DocAlias
from ietf.codestand import constants
from ietf.codestand.matches.forms import SearchForm, ProjectContainerForm, ContactForm
from ietf.codestand.requests.forms import CodeRequestForm, DocNameForm, TagForm, MentorForm
from ietf.codestand.matches.models import ProjectContainer, ProjectTag, ProjectContact
from ietf.codestand.helpers.utils import (render_page, is_user_allowed, clear_session, get_user)


def show_list(request, type_list="all", att=constants.ATT_CREATION_DATE, state="False", page=1):
    """ List all CodeRequests
        :param page: 
        :param state: string - if the state is true then the project_containers
                               has been previously loaded (eg. Loaded from the search)
        :param att: string - List will be sorted by this attribute (eg. if creation_date then ordered by date)
        :param type_list: string - (all = All CodeRequests / mylist = CodeRequests I've Created /
                                    mentoring = CodeRequests i'm mentoring)
        :param request: HttpResponse
    """
    
    user = get_user(request)
    user_id = None
    if user:
        user_id = user.id
    if state == "True" and constants.ALL_PROJECTS in request.session:
        project_containers = request.session[constants.ALL_PROJECTS]
        request.session[constants.MAINTAIN_STATE] = True
    else:
        if type_list == "mylist":
            # Project must have been created by the current user and user must have permission mentor
            if not is_user_allowed(user, "iscreator"):
                raise Http404
            project_containers = ProjectContainer.objects.exclude(is_deleted=True).exclude(code_request__isnull=True).filter(
                owner=user.id)
        elif type_list == "mentoring":
            # Project must have been mentored by the current user and user must have permission mentor
            if not is_user_allowed(user, "ismentor"):
                raise Http404
            project_containers = ProjectContainer.objects.exclude(is_deleted=True).exclude(code_request__isnull=True).filter(
                code_request__mentor=user.id)
        else:
            # Exclude ProjectContainers that don't have an associated CodeRequest (TODO: Centralize this?)
            project_containers = ProjectContainer.objects.exclude(is_deleted=True).exclude(code_request__isnull=True)

    if att == constants.STRING_POPULARITY:
        project_containers = project_containers.annotate(count=Count('codings')).order_by('-count')[:20]
    else:
        if att != constants.ATT_WORKING_GROUP and att != constants.ATT_AREA:
            project_containers = project_containers.order_by(att)
    list_of_lists = []

    paginator = Paginator(project_containers, 5)
    page = int(page)
    project_containers = paginator.page(page)

    # Attributes that should grouping
    map_attributes = {'protocol': constants.STRING_PROTOCOL,
                      'working_group': constants.STRING_WORKINGGROUP,
                      'area': constants.STRING_AREA}
    
    all_documents = []
    # If the attribute is in the dictionary then should do the sorting and grouping for this attribute
    if att in map_attributes:
        # Get all values for this attribute (eg. protocol: OSPF, RIP, NewProtocol)
        if att == 'protocol':
            select = []
            for proj in project_containers:
                select.append(proj.protocol)
            select = list(set(select))
        else:
            docs = []
            keys = []
            for project_container in project_containers:
                if project_container.docs:
                    keys += filter(None, project_container.docs.split(';'))
            keys = list(set(keys))
            all_documents = list(
                DocAlias.objects.using('datatracker').filter(name__in=keys)
                                                     .values_list('name', 'document__group__name',
                                                                  'document__group__parent__name'))
            for p in project_containers:
                keys = []
                if p.docs:
                    keys = filter(None, p.docs.split(';'))
                for name, gname, gparentname in all_documents:
                    for key in keys:
                        if key == name:
                            if map_attributes[att] == constants.STRING_WORKINGGROUP:
                                docs.append(gname)
                            else:
                                docs.append(gparentname)
            select = list(set(docs))

        for s in select:
            compare = None
            new_projs = []
            val = map_attributes[att]
            for p in project_containers:
                if (p.is_archived and p.owner != user_id) or p.is_deleted:
                    continue
                elif att == constants.STRING_PROTOCOL:
                    compare = s.upper()
                    prop = getattr(p, val).upper()  # Get Protocol name
                else:
                    compare = s
                    prop = None
                    if p.docs:
                        keys = filter(None, p.docs.split(';'))
                    else:
                        continue
                    # docs = DocAlias.objects.using('datatracker').filter(name__in=keys)
                    for name, gname, gparentname in all_documents:
                        for key in keys:
                            if key == name:
                                if val == constants.STRING_WORKINGGROUP:
                                    prop = gname  # Get working group name
                                    break
                                else:
                                    prop = gparentname  # Get area name
                                    break
                if prop is not None and p not in new_projs and prop == compare:
                    new_projs.append(p)
            if len(new_projs) > 0 and not any(compare in comp[1] for comp in list_of_lists):
                list_of_lists.append((new_projs, compare))
    else:  # Just show all CodeRequests in order
        for p in project_containers:
            if (not p.is_archived or p.owner == user_id) and not p.is_deleted:
                new_projs = [p]
                list_of_lists.append((new_projs, ""))

    return render_page(request, constants.TEMPLATE_REQUESTS_LIST, {
        'projectcontainers': list_of_lists,
        'owner': user,
        'numpages': paginator.num_pages,
        'pages': range(1, paginator.num_pages + 1),
        'hasnext': project_containers.has_next(),
        'hasprevious': project_containers.has_previous(),
        'page': page,
        'attribute': att,
        'typelist': type_list,
        'state': state,
        'template': 'ietf.codestand.requests.views.show_list'
    })


def search(request, type_list="all"):
    """ Shows the list of CodeProjects, filtering according to the selected checkboxes
        :param request: HttpResponse
        :param type_list: string - Which template is selected (eg. all or mymatches)
    """

    search_type = request.GET.get("submit")
    if search_type:

        # get query field
        query = ''
        if request.GET.get(search_type):
            query = request.GET.get(search_type)

        ids = []

        valid_searches = [constants.STRING_TITLE, constants.STRING_DESCRIPTION, constants.STRING_PROTOCOL,
                          constants.STRING_MENTOR, constants.STRING_AREA, constants.STRING_WORKINGGROUP,
                          constants.STRING_DOC]

        search_in_all = True
        for v in valid_searches:
            if v in request.GET:
                search_in_all = False
                break

        if search_in_all or request.GET.get(constants.STRING_TITLE):
            ids += ProjectContainer.objects.exclude(is_deleted=True).exclude(code_request__isnull=True).filter(
                title__icontains=query).values_list('id', flat=True)

        if search_in_all or request.GET.get(constants.STRING_DESCRIPTION):
            ids += ProjectContainer.objects.exclude(is_deleted=True).exclude(code_request__isnull=True).filter(
                description__icontains=query).values_list('id', flat=True)

        if search_in_all or request.GET.get(constants.STRING_PROTOCOL):
            ids += ProjectContainer.objects.exclude(is_deleted=True).exclude(code_request__isnull=True).filter(
                protocol__icontains=query).values_list('id', flat=True)

        if search_in_all or request.GET.get(constants.STRING_MENTOR):
            projects = ProjectContainer.objects.exclude(is_deleted=True).exclude(code_request__isnull=True)
            for pr in projects:
                # TODO: Review this
                try:
                    user = Person.objects.using('datatracker').get(id=pr.code_request.mentor)
                except:
                    user = None
                if user and query.lower() in user.name.lower():
                    ids.append(pr.id)

        if search_in_all or request.GET.get(constants.STRING_DOC):
            docs = []
            for project_container in ProjectContainer.objects.exclude(is_deleted=True).exclude(code_request__isnull=True).all():
                if not project_container.docs or project_container.docs == '':
                    continue
                keys = filter(None, project_container.docs.split(';'))
                docs.extend(
                    list(DocAlias.objects.using('datatracker').filter(name__in=keys).values_list('document__name')))
                for doc in docs:
                    if query.lower() in doc[0].lower():
                        ids.append(project_container.id)
                        break

        if search_in_all or request.GET.get(constants.STRING_AREA):
            docs = []
            for project_container in ProjectContainer.object.exclude(is_deleted=True).all():
                if not project_container.docs or project_container.docs == '':
                    continue
                keys = filter(None, project_container.docs.split(';'))
                docs.extend(list(DocAlias.objects.using('datatracker').filter(name__in=keys).values_list(
                    'document__group__parent__name')))
                for doc in docs:
                    if query.lower() in doc[0].lower():
                        ids.append(project_container.id)
                        break

        if search_in_all or request.GET.get(constants.STRING_WORKINGGROUP):
            docs = []
            for project_container in ProjectContainer.objects.exclude(is_deleted=True).all():
                if not project_container.docs or project_container.docs == '':
                    continue
                keys = filter(None, project_container.docs.split(';'))
                docs.extend(list(
                    DocAlias.objects.using('datatracker').filter(name__in=keys).values_list('document__group__name')))
                for doc in docs:
                    if query.lower() in doc[0].lower():
                        ids.append(project_container.id)
                        break

        project_containers = ProjectContainer.objects.exclude(is_deleted=True).filter(id__in=list(set(ids)))

        request.session[constants.ALL_PROJECTS] = project_containers

        request.session[constants.MAINTAIN_STATE] = True

        return HttpResponseRedirect(
            settings.CODESTAND_PREFIX + '/codestand/requests/show_list/' + 
            type_list + '/{0}/'.format(constants.ATT_CREATION_DATE) + 'True')
    else:
        return render_page(request, constants.TEMPLATE_REQUESTS_SEARCH, {
            "form": SearchForm()
        })


def show(request, pk):
    """ Show individual Codestand Project
        :param request: HttpResponse
        :param pk: int - Indicates which project must be loaded
    """

    project_container = get_object_or_404(ProjectContainer, id=pk)

    areas = []
    working_groups = []
    docs = []

    user = get_user(request)
    mentor = None
    if project_container.code_request.mentor:
        mentor = Person.objects.using('datatracker').get(id=project_container.code_request.mentor)

    # According to model areas and working groups should come from documents
    keys = []
    if project_container.docs:
        keys = filter(None, project_container.docs.split(';'))
    docs = list(DocAlias.objects.using('datatracker').filter(name__in=keys).values_list('name', 'document__group__name',
                                                                                        'document__group__parent__name'))
    for name, gname, gparentname in docs:
        if gname not in working_groups:
            working_groups.append(gname)
        if gparentname:
            if gparentname not in areas:
                areas.append(gparentname)  # use acronym?
        else:
            areas.append(gname)

    if not areas:
        areas = [constants.STRING_NONE]
    if not working_groups:
        working_groups = [constants.STRING_NONE]

    return render_page(request, constants.TEMPLATE_REQUESTS_SHOW, {
        'projectcontainer': project_container,
        'areas': areas,
        'workinggroups': working_groups,
        'docs': docs,
        'owner': user,
        'mentor': mentor,
        'list_template': constants.TEMPLATE_REQUESTS_LIST
    })


def save_project(request, template, project_container=None):
    """ Used to create or update a CodeRequest.
        When project container is null then a new
        instance is created in the database
        :param request: HttpResponse
        :param template: string
        :param project_container: ProjectContainer
    """

    # NOTE: Is slow 'cause of the mentors list (?)

    user = get_user(request)

    doc_form = DocNameForm()
    tag_form = modelform_factory(ProjectTag, form=TagForm)

    # TODO: check permission
    can_add_documents = is_user_allowed(user, "canadddocuments")
    can_add_tags = is_user_allowed(user, "canaddtags")
    can_add_contact = is_user_allowed(user, "canaddcontact")

    # If not there in the current session then should be setted a default
    proj_form = request.session[
        constants.PROJECT_INSTANCE] if constants.PROJECT_INSTANCE in request.session else ProjectContainerForm()
    req_form = request.session[
        constants.REQUEST_INSTANCE] if constants.REQUEST_INSTANCE in request.session else CodeRequestForm()
    contact_form = request.session[
        constants.CONTACT_INSTANCE] if constants.CONTACT_INSTANCE in request.session else ContactForm()
    mentor_form = request.session[
        constants.MENTOR_INSTANCE] if constants.MENTOR_INSTANCE in request.session else MentorForm()
    is_mentor = request.session[constants.IS_MENTOR] if constants.IS_MENTOR in request.session else False

    docs = request.session[constants.ADD_DOCS]
    tags = request.session[constants.ADD_TAGS]
    contacts = request.session[constants.ADD_CONTACTS]

    previous_template = "codestand/requests/show_list"

    if constants.PREVIOUS_TEMPLATE not in request.session:
        request.session[constants.PREVIOUS_TEMPLATE] = previous_template

    if request.method == 'POST':

        doc_name = request.POST.get("doc")
        if request.POST.get("chkMentor"):
            is_mentor = True
            mentor_id = Person.objects.using('datatracker').get(id=user.id).id
        else:
            is_mentor = False
            mentor_id = request.POST.get("mentor")

        if mentor_id:
            selected_mentor = Person.objects.using('datatracker').get(id=mentor_id)
            mentor_form = MentorForm(initial={'mentor': selected_mentor})
        else:
            mentor_form = MentorForm()

        tag = TagForm(request.POST)
        new_contact = ContactForm(request.POST)

        if project_container is not None:
            new_proj = ProjectContainerForm(request.POST, instance=project_container)
            new_req = CodeRequestForm(request.POST, instance=project_container.code_request)
        else:
            new_proj = ProjectContainerForm(request.POST)
            new_req = CodeRequestForm(request.POST)

        # Adding document to the documents list to be saved in the project
        if request.POST.get(constants.STRING_DOC) and doc_name:
            selected_document = DocAlias.objects.using('datatracker').filter(name=doc_name)
            if selected_document:
                new_doc = selected_document[0]
                docs.append(new_doc)  # Updating documents to appear after rendering

        # Adding new tag to the tags list to be saved in the project
        elif request.POST.get(constants.STRING_TAG) and tag.is_valid():
            new_tag = tag.save(commit=False)
            new_tag.name = "#" + new_tag.name
            tags.append(new_tag)  # Updating tags to appear after rendering

        # Adding new contact to the mailing list to be saved in the project
        elif request.POST.get(constants.STRING_CONTACT) and new_contact.is_valid():
            m = new_contact.save(commit=False)
            if m.type.lower() == constants.STRING_TWITTER:  # TODO: Standardize for all
                m.contact = '@' + m.contact
            contacts.append(m)

        # Saving project (new or not) in the database
        elif request.POST.get(constants.STRING_SAVE) and new_proj.is_valid() and new_req.is_valid():
            # Creating new (or update) instance of the code request in the database
            code_request = new_req.save(commit=False)
            if mentor_id:
                code_request.mentor = mentor_id
            code_request.save()
            # Creating new (or update) instance of the project container in the database
            project = new_proj.save(commit=False)
            project.owner = Person.objects.using('datatracker').get(user=request.user).id  # Set creator
            project.code_request = code_request  # Linking CodeRequest to Project
            project.save()

            modified = False

            rem_docs = request.session[constants.REM_DOCS]
            rem_tags = request.session[constants.REM_TAGS]
            rem_contacts = request.session[constants.REM_CONTACTS]

            for doc in rem_docs:
                project.docs = project.docs.replace(doc.name + ';', '', 1)
                modified = True

            for tag in rem_tags:
                project.tags.remove(tag)
                modified = True

            for m in rem_contacts:
                project.contacts.remove(m)
                modified = True

            for doc in docs:
                keys = project.docs
                if keys is None:
                    project.docs = '{};'.format(doc.name)
                else:
                    if doc.name not in project.docs:
                        project.docs += '{};'.format(doc.name)
                modified = True

            for m in contacts:
                try:
                    # Trying get an existing contact
                    new_m = ProjectContact.objects.get(contact=m.contact, type=m.type)
                except:
                    # Otherwise you need to create a new contact
                    m.save()
                    new_m = m

                project.contacts.add(new_m)
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
                project.tags.add(new_tag)
                modified = True

            if modified:
                project.save()

            return HttpResponseRedirect(settings.CODESTAND_PREFIX + '/codestand/requests/' + str(project.id))

        # Updating session variables
        request.session[constants.PROJECT_INSTANCE] = new_proj
        request.session[constants.REQUEST_INSTANCE] = new_req
        request.session[constants.MENTOR_INSTANCE] = mentor_form
        request.session[constants.IS_MENTOR] = is_mentor

        proj_form = new_proj
        req_form = new_req

    return render_page(request, template, {
        'projectcontainer': project_container,
        'projform': proj_form,
        'checked': is_mentor,
        'reqform': req_form,
        'contactform': contact_form,
        'docform': doc_form,
        'tagform': tag_form,
        'mentorform': mentor_form,
        'docs': docs,
        'tags': tags,
        'contacts': contacts,
        'canadddocuments': can_add_documents,
        'canaddtags': can_add_tags,
        'canaddcontact': can_add_contact
    })


''' TODO: UNIFICAR CODIGO MATCHES E REQUESTS '''


@login_required(login_url=settings.CODESTAND_PREFIX + constants.TEMPLATE_LOGIN)
def archive(request, pk):
    
    project_container = get_object_or_404(ProjectContainer, id=pk)
    
    user = get_user(request)
    if project_container.owner != user.id:
        raise Http404
    
    project_container.is_archived = not project_container.is_archived
    project_container.save()
    
    refresh_template = request.session[constants.ACTUAL_TEMPLATE]
    return HttpResponseRedirect(refresh_template)


@login_required(login_url=settings.CODESTAND_PREFIX + constants.TEMPLATE_LOGIN)
def edit(request, pk):
    """ Edit CodeRequest Entry
        :param request: HttpResponse
        :param pk: int - indicates which project must be loaded
    """

    project_container = get_object_or_404(ProjectContainer, id=pk)

    if request.path != request.session[constants.ACTUAL_TEMPLATE]:
        clear_session(request)
        request.session[constants.REM_DOCS] = []
        request.session[constants.REM_CONTACTS] = []
        request.session[constants.REM_TAGS] = []

    request.session[constants.MAINTAIN_STATE] = True

    # Fills session variables with project values already saved

    if constants.ADD_DOCS not in request.session:
        docs = []
        if project_container.docs:
            keys = filter(None, project_container.docs.split(';'))
            for key in keys:
                docs.append(DocAlias.objects.using('datatracker').get(name=key))
        request.session[constants.ADD_DOCS] = list(docs)

    if constants.ADD_TAGS not in request.session:
        tags = project_container.tags.all()
        request.session[constants.ADD_TAGS] = list(tags)

    if constants.ADD_CONTACTS not in request.session:
        contacts = project_container.contacts.all()
        request.session[constants.ADD_CONTACTS] = list(contacts)

    # TODO: Review this        
    us = get_user(request)
    user = us

    # Project must have been created by the current user and
    # User must have permission to add new CodeRequest
    if project_container.owner != user.id:
        raise Http404

    # Save project and code request in the cache to make 'update' and 'new' use the same code (save_project)
    request.session[constants.PROJECT_INSTANCE] = ProjectContainerForm(instance=project_container)
    request.session[constants.REQUEST_INSTANCE] = CodeRequestForm(instance=project_container.code_request)
    if project_container.code_request.mentor:
        if project_container.code_request.mentor == user.id:
            request.session[constants.IS_MENTOR] = True
        else:
            selected_mentor = Person.objects.using('datatracker').get(id=project_container.code_request.mentor)
            mentor_form = MentorForm(initial={'mentor': selected_mentor})
            request.session[constants.MENTOR_INSTANCE] = mentor_form

    return save_project(request, constants.TEMPLATE_REQUESTS_EDIT, project_container)


@login_required(login_url=settings.CODESTAND_PREFIX + constants.TEMPLATE_LOGIN)
def new(request):
    """ New CodeRequest Entry
        :param request: HttpResponse
    """

    if request.path != request.session[constants.ACTUAL_TEMPLATE]:
        clear_session(request)
        request.session[constants.REM_DOCS] = []
        request.session[constants.REM_TAGS] = []
        request.session[constants.REM_CONTACTS] = []
        request.session[constants.ADD_CONTACTS] = []
        request.session[constants.ADD_DOCS] = []
        request.session[constants.ADD_TAGS] = []

    request.session[constants.MAINTAIN_STATE] = True

    return save_project(request, constants.TEMPLATE_REQUESTS_NEW)


@login_required(login_url=settings.CODESTAND_PREFIX + constants.TEMPLATE_LOGIN)
def delete(request, pk, template=None):
    
    project = get_object_or_404(ProjectContainer, id=pk)
    user = get_user(request)
    if project.owner != user.id:
        raise Http404
    project.is_deleted = True
    project.save()
    
    if not template:
        template = request.session[constants.ACTUAL_TEMPLATE]
        HttpResponseRedirect(template)
    else:
        return HttpResponseRedirect('/codestand/requests/show_list/')


@login_required(login_url=settings.CODESTAND_PREFIX + constants.TEMPLATE_LOGIN)
def remove_contact(request, pk, contact_name):
    """ Adds the removal list, but will only be removed when saving changes
        pk (pk = 0 - new ProjectContainer / pk > 0 - edit ProjectContainer
        :param request: HttpResponse
        :param pk: int - Indicates which project must be loaded
        :param contact_name: string - Indicates which contact must be loaded
    """

    refresh_template = request.session[constants.ACTUAL_TEMPLATE]

    contacts = request.session[constants.ADD_CONTACTS]
    contact = next(el for el in contacts if el.contact == contact_name)

    if pk != "0":
        project_container = get_object_or_404(ProjectContainer, id=pk)

        # TODO: Review this        
        us = get_user(request)
        user = us

        # Project must have been created by the current user and
        # User must have permission to add new CodeRequest
        if project_container.owner != user.id:
            raise Http404

        if project_container.contacts.filter(contact=contact_name):
            cache_list = request.session[constants.REM_CONTACTS]
            cache_list.append(contact)

    contacts.remove(contact)
    request.session[constants.ADD_CONTACTS] = contacts

    # TODO: Centralize this?
    return HttpResponseRedirect(refresh_template)


@login_required(login_url=settings.CODESTAND_PREFIX + constants.TEMPLATE_LOGIN)
def remove_document(request, pk, doc_name):
    """ Adds the removal list, but will only be removed when saving changes
        pk (pk = 0 - new ProjectContainer / pk > 0 - edit ProjectContainer
        :param request: HttpResponse
        :param pk: int - Indicates which project must be loaded
        :param doc_name: string - Indicates which doc must be removed
    """

    refresh_template = request.session[constants.ACTUAL_TEMPLATE]

    docs = request.session[constants.ADD_DOCS]
    document = next(el for el in docs if el.name == doc_name)

    if pk != "0":
        project_container = get_object_or_404(ProjectContainer, id=pk)

        # TODO: Review this        
        us = get_user(request)
        user = us

        # Project must have been created by the current user and
        # User must have permission to add new CodeRequest
        if project_container.owner != user.id:
            raise Http404

        if doc_name in project_container.docs:
            cache_list = request.session[constants.REM_DOCS]
            cache_list.append(document)

    docs.remove(document)
    request.session[constants.ADD_DOCS] = docs

    # TODO: Centralize this?
    return HttpResponseRedirect(refresh_template)


@login_required(login_url=settings.CODESTAND_PREFIX + constants.TEMPLATE_LOGIN)
def remove_tag(request, pk, tag_name):
    """ Adds the removal list, but will only be removed when saving changes
        pk (0 = new ProjectContainer / 0 >= edit ProjectContainer
        :param request: HttpResponse
        :param pk: int - Indicates which project must be loaded
        :param tag_name: string - Indicates which tag must be removed
    """

    refresh_template = request.session[constants.ACTUAL_TEMPLATE]

    tags = request.session[constants.ADD_TAGS]
    tag = next(el for el in tags if el.name == tag_name)

    if pk != "0":
        project_container = get_object_or_404(ProjectContainer, id=pk)

        # TODO: Review this        
        us = get_user(request)
        user = us

        # Project must have been created by the current user and
        # User must have permission to add new CodeRequest
        if project_container.owner != user.id:
            raise Http404

        if project_container.tags.filter(name=tag_name):
            cache_list = request.session[constants.REM_TAGS]
            cache_list.append(tag)

    tags.remove(tag)
    request.session[constants.ADD_TAGS] = tags

    # TODO: Centralize this?
    return HttpResponseRedirect(refresh_template)
