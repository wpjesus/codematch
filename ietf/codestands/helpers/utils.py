from ietf.codestands import constants
from django.shortcuts import render
from ietf.person.models import Person, Alias
from ietf.codestands.matches.models import ProjectContainer, CodingProject


# ----------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------
def is_user_allowed(user, permission):
    """ Check if the user has permission
        :param permission:
        :param user:
    """
    print user, permission
    return True


def get_user(request):
    # TODO: Colocar o usuario nas variaveis de sessao
    if constants.USER not in request.session or request.session[constants.USER].user != request.user:
        if request.user.is_authenticated():
            user = Person.objects.using('datatracker').get(user=request.user)
            request.session[constants.USER] = user
            return user
        else:
            return None
    else:
        return request.session[constants.USER]

def get_menu_arguments(request, keys):
    user = get_user(request)

    # Always setted
    keys['from'] = request.GET.get('from', None)
    keys['codestands_version'] = constants.VERSION
    keys['codestands_revision_date'] = constants.RELEASE_DATE

    if user is not None:  # Only when user is logged

        my_codings = CodingProject.objects.filter(coder=user.id)
        my_own_projects = ProjectContainer.objects.filter(owner=user.id)
        my_mentoring_projects = ProjectContainer.objects.filter(code_request__mentor=user.id)

        # Some tests are made on the templates, should be here in the code?

        keys["mycodings"] = my_codings
        keys["projectsowner"] = my_own_projects
        keys["projectsmentoring"] = my_mentoring_projects

        keys["canaddcoding"] = is_user_allowed(user, "canaddcoding")
        keys["canaddrequest"] = is_user_allowed(user, "canaddrequest")
        keys["ismentor"] = is_user_allowed(user, "ismentor")

        # Try get pretty name user (otherwise, email will be used)
        alias = Alias.objects.using('datatracker').filter(person=user)

        alias_name = alias[0].name if alias else user.name

        keys["username"] = alias_name

    return keys


def clear_session(request):
    # All session variables
    keys = [constants.ALL_PROJECTS, constants.PROJECT_INSTANCE, constants.REQUEST_INSTANCE, constants.CONTACT_INSTANCE,
            constants.ACTUAL_PROJECT, constants.MENTOR_INSTANCE, constants.IS_MENTOR,
            constants.CODE_INSTANCE, constants.ADD_DOCS, constants.ADD_TAGS, constants.ADD_LINKS,
            constants.ADD_CONTACTS,
            constants.REM_CONTACTS, constants.REM_DOCS, constants.REM_TAGS, constants.REM_LINKS]

    # If MAINTAIN_STATE is true then session variables shouldn't be deleted
    if constants.MAINTAIN_STATE in request.session and request.session[constants.MAINTAIN_STATE] == True:
        del request.session[constants.MAINTAIN_STATE]
    else:  # Otherwise all session variables must be erased
        for key in keys:
            if key in request.session:
                del request.session[key]


def render_page(request, template, keys=None):
    """ Special method for rendering pages
        :param keys:
        :param template:
        :param request:
    """
    if not keys:
        keys = {}

    clear_session(request)

    # if the template has changed then update actual and previous templates
    if constants.ACTUAL_TEMPLATE in request.session:
        actual_template = request.session[constants.ACTUAL_TEMPLATE]
        previous_template = ''
        if constants.PREVIOUS_TEMPLATE in request.session:
            previous_template = request.session[constants.PREVIOUS_TEMPLATE]
        if actual_template != request.path:
            # TODO: Melhorar isto, mas no search existe referencia circular
            if not ('search' in previous_template and 'show_list' in actual_template):
                request.session[constants.PREVIOUS_TEMPLATE] = actual_template

    request.session[constants.ACTUAL_TEMPLATE] = request.path

    return render(request, template, get_menu_arguments(request, keys))
