from ietf.codematch import constants
from django.shortcuts import get_object_or_404
from django.forms.models import modelform_factory
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from ietf.person.models import Person
from ietf.doc.models import DocAlias
from ietf.codematch.matches.forms import SearchForm, ProjectContainerForm, ContactForm
from ietf.codematch.requests.forms import CodeRequestForm, DocNameForm, TagForm
from ietf.codematch.matches.models import ProjectContainer, ProjectTag, ProjectContact
from ietf.codematch.helpers.utils import (render_page, is_user_allowed, clear_session, get_user)
from django.conf import settings


def show_list(request, type_list="all", att=constants.ATT_CREATION_DATE, state=""):
    """ List all CodeRequests
        type_list (all = All CodeRequests / mylist = CodeRequests I've Created / mentoring = CodeRequests i'm mentoring)
        att = List will be sorted by this attribute (eg. if creation_date then ordered by date)
        state = if the state is true then the project_containers has been previously loaded (eg. Loaded from the search)
        :param state:
        :param att:
        :param type_list:
        :param request:
    """

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
            project_containers = ProjectContainer.objects.exclude(code_request__isnull=True).filter(
                code_request__mentor=user)
        else:
            # Exclude ProjectContainers that don't have an associated CodeRequest (TODO: Centralize this?)
            project_containers = ProjectContainer.objects.exclude(code_request__isnull=True)

    if att == constants.STRING_POPULARITY:
        project_containers = project_containers.annotate(count=Count('codings')).order_by('-count')[:20]
    else:
        project_containers = project_containers.order_by(att)[:20]

    list_of_lists = []

    # Attributes that should grouping
    map_attributes = {'protocol': constants.STRING_PROTOCOL,
                      'docs__document__group__name': constants.STRING_WORKINGGROUP,
                      'docs__document__group__parent__name': constants.STRING_AREA}

    # If the attribute is in the dictionary then should do the sorting and grouping for this attribute
    if att in map_attributes:
        # Get all values for this attribute (eg. protocol: OSPF, RIP, NewProtocol)
        select = list(set(project_containers.values_list(att, flat=True)))
        for s in select:
            new_projs = []
            val = map_attributes[att]
            for p in project_containers:
                if att == constants.STRING_PROTOCOL:
                    prop = getattr(p, val)  # Get Protocol name
                else:
                    prop = None
                    for d in p.docs.all():
                        if val == constants.STRING_WORKINGGROUP:
                            prop = d.document.group.name  # Get working group name
                        else:
                            prop = d.document.group.parent.name  # Get area name
                if prop is not None and p not in new_projs and prop == s:
                    new_projs.append(p)
            if len(new_projs) > 0:
                list_of_lists.append((new_projs, s))
    else:  # Just show all CodeRequests in order
        for p in project_containers:
            new_projs = [p]
            list_of_lists.append((new_projs, ""))

    return render_page(request, constants.TEMPLATE_REQUESTS_LIST, {
        'projectcontainers': list_of_lists,
        'owner': user,
        'attribute': att,
        'typelist': type_list,
        'state': state,
        'template': 'ietf.codematch.requests.views.show_list'
    })


def search(request, type_list="all"):
    """ Shows the list of CodeProjects, filtering according to the selected checkboxes
        :param type_list:
        :param request:
    """

    search_type = request.GET.get("submit")
    if search_type:

        # get query field
        query = ''
        if request.GET.get(search_type):
            query = request.GET.get(search_type)

        ids = []

        if request.GET.get(constants.STRING_TITLE):
            ids += ProjectContainer.objects.exclude(code_request__isnull=True).filter(
                title__icontains=query).values_list('id', flat=True)

        if request.GET.get(constants.STRING_DESCRIPTION):
            ids += ProjectContainer.objects.exclude(code_request__isnull=True).filter(
                description__icontains=query).values_list('id', flat=True)

        if request.GET.get(constants.STRING_PROTOCOL):
            ids += ProjectContainer.objects.exclude(code_request__isnull=True).filter(
                protocol__icontains=query).values_list('id', flat=True)

        if request.GET.get(constants.STRING_MENTOR):
            ids += ProjectContainer.objects.exclude(code_request__isnull=True).filter(
                code_request__mentor__name__icontains=query).values_list('id', flat=True)

        if request.GET.get(constants.STRING_DOCS):
            ids += ProjectContainer.objects.exclude(code_request__isnull=True).filter(
                docs__name__icontains=query).values_list('id', flat=True)

        if request.GET.get(constants.STRING_AREA):
            ids += ProjectContainer.objects.exclude(code_request__isnull=True).filter(
                docs__document__group__parent__name__icontains=query).values_list('id', flat=True)

        if request.GET.get(constants.STRING_WORKINGGROUP):
            ids += ProjectContainer.objects.exclude(code_request__isnull=True).filter(
                docs__document__group__name__icontains=query).values_list('id', flat=True)

        project_containers = ProjectContainer.objects.filter(id__in=list(set(ids)))

        request.session[constants.ALL_PROJECTS] = project_containers

        request.session[constants.MAINTAIN_STATE] = True

        return HttpResponseRedirect(
            settings.CODEMATCH_PREFIX + '/codematch/requests/show_list/' + type_list + '/creation_date/' + 'True')
    else:
        return render_page(request, constants.TEMPLATE_REQUESTS_SEARCH, {
            "form": SearchForm()
        })


def show(request, pk):
    """ Show individual Codematch Project
        :param pk:
        :param request:
    """

    project_container = get_object_or_404(ProjectContainer, id=pk)

    areas = []
    working_groups = []

    user = get_user(request)

    # According to model areas and working groups should come from documents
    for doc in project_container.docs.all():
        group = doc.document.group
        if group.name not in working_groups:
            working_groups.append(group.name)
        if group.parent:
            if group.parent.name not in areas:
                areas.append(group.parent.name)  # use acronym?
        else:
            areas.append(group.name)

    if not areas:
        areas = [constants.STRING_NONE]
    if not working_groups:
        working_groups = [constants.STRING_NONE]

    return render_page(request, constants.TEMPLATE_REQUESTS_SHOW, {
        'projectcontainer': project_container,
        'areas': areas,
        'workinggroups': working_groups,
        'owner': user
    })


def save_project(request, template, project_container=None):
    """ Used to create or update a CodeRequest.
        When project container is null then a new
        instance is created in the database
        :param project_container:
        :param template:
        :param request:
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

    docs = request.session[constants.ADD_DOCS]
    tags = request.session[constants.ADD_TAGS]
    contacts = request.session[constants.ADD_CONTACTS]

    previous_template = "codematch/requests/show_list"

    if constants.PREVIOUS_TEMPLATE not in request.session:
        request.session[constants.PREVIOUS_TEMPLATE] = previous_template

    if request.method == 'POST':

        doc_name = request.POST.get("doc")
        tag = TagForm(request.POST)
        new_contact = ContactForm(request.POST)

        if project_container is not None:
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
            new_tag.name = "#" + new_tag.name
            tags.append(new_tag)  # Updating tags to appear after rendering

        # Adding new contact to the mailing list to be saved in the project
        elif new_contact.is_valid():
            m = new_contact.save(commit=False)
            if m.type.lower() == constants.STRING_TWITTER:  # TODO: Padronize for all
                m.contact = '@' + m.contact
            contacts.append(m)

        # Saving project (new or not) in the database
        elif request.POST.get('save') and new_proj.is_valid() and new_req.is_valid():
            # Creating new (or update) instance of the code request in the database
            code_request = new_req.save()
            # Creating new (or update) instance of the project container in the database
            project = new_proj.save(commit=False)
            project.owner = Person.objects.get(user=request.user)  # Set creator
            project.code_request = code_request  # Linking CodeRequest to Project
            project.save()

            modified = False

            rem_docs = request.session[constants.REM_DOCS]
            rem_tags = request.session[constants.REM_TAGS]
            rem_contacts = request.session[constants.REM_CONTACTS]

            for doc in rem_docs:
                project.docs.remove(doc)
                modified = True

            for tag in rem_tags:
                project.tags.remove(tag)
                modified = True

            for m in rem_contacts:
                project.contacts.remove(m)
                modified = True

            for doc in docs:
                project.docs.add(doc)
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

            return HttpResponseRedirect(settings.CODEMATCH_PREFIX + '/codematch/requests/' + str(project.id))

        # Updating session variables
        request.session[constants.PROJECT_INSTANCE] = new_proj
        request.session[constants.REQUEST_INSTANCE] = new_req

        proj_form = new_proj
        req_form = new_req

    return render_page(request, template, {
        'projectcontainer': project_container,
        'projform': proj_form,
        'reqform': req_form,
        'contactform': contact_form,
        'docform': doc_form,
        'tagform': tag_form,
        'docs': docs,
        'tags': tags,
        'contacts': contacts,
        'canadddocuments': can_add_documents,
        'canaddtags': can_add_tags,
        'canaddcontact': can_add_contact
    })


@login_required(login_url=settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def edit(request, pk):
    """ Edit CodeRequest Entry
        :param pk:
        :param request:
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
        docs = project_container.docs.all()
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
    if project_container.owner != user:
        raise Http404

    # Save project and code request in the cache to make 'update' and 'new' use the same code (save_project)
    request.session[constants.PROJECT_INSTANCE] = ProjectContainerForm(instance=project_container)
    request.session[constants.REQUEST_INSTANCE] = CodeRequestForm(instance=project_container.code_request)

    return save_project(request, constants.TEMPLATE_REQUESTS_EDIT, project_container)


@login_required(login_url=settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def new(request):
    """ New CodeRequest Entry
        :param request:
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


@login_required(login_url=settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def remove_contact(request, pk, contact_name):
    """ Adds the removal list, but will only be removed when saving changes
        pk (pk = 0 - new ProjectContainer / pk > 0 - edit ProjectContainer
        :param contact_name:
        :param pk:
        :param request:
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
        if project_container.owner != user:
            raise Http404

        if project_container.contacts.filter(contact=contact_name):
            cache_list = request.session[constants.REM_CONTACTS]
            cache_list.append(contact)

    contacts.remove(contact)
    request.session[constants.ADD_CONTACTS] = contacts

    # TODO: Centralize this?
    return HttpResponseRedirect(refresh_template)


@login_required(login_url=settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def remove_document(request, pk, doc_name):
    """ Adds the removal list, but will only be removed when saving changes
        pk (pk = 0 - new ProjectContainer / pk > 0 - edit ProjectContainer
        :param doc_name:
        :param pk:
        :param request:
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
        if project_container.owner != user:
            raise Http404

        if project_container.docs.filter(name=doc_name):
            cache_list = request.session[constants.REM_DOCS]
            cache_list.append(document)

    docs.remove(document)
    request.session[constants.ADD_DOCS] = docs

    # TODO: Centralize this?
    return HttpResponseRedirect(refresh_template)


@login_required(login_url=settings.CODEMATCH_PREFIX + constants.TEMPLATE_LOGIN)
def remove_tag(request, pk, tag_name):
    """ Adds the removal list, but will only be removed when saving changes
        pk (0 = new ProjectContainer / 0 >= edit ProjectContainer :param tag_name:
        :param tag_name:
        :param pk:
        :param request:
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
        if project_container.owner != user:
            raise Http404

        if project_container.tags.filter(name=tag_name):
            cache_list = request.session[constants.REM_TAGS]
            cache_list.append(tag)

    tags.remove(tag)
    request.session[constants.ADD_TAGS] = tags

    # TODO: Centralize this?
    return HttpResponseRedirect(refresh_template)
