from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from ietf.codestand.helpers.utils import (render_page, get_user)
from ietf.codestand import constants
from ietf.codestand.matches.models import DashboardConfig
from ietf.codestand.dashboard import (get_my_matches, get_my_requests, get_all_matches)


def index(request):
    return render_page(request, constants.TEMPLATE_INDEX)


def about(request):
    return render_page(request, constants.TEMPLATE_ABOUT)


def back(request):
    template = "/codestand/"

    if "previous_template" in request.session:
        template = request.session["previous_template"]

    return HttpResponseRedirect(template)


def dashboard(request):
    methods = [get_my_matches, get_my_requests, get_all_matches]
    user = get_user(request)
    items = []
    keys = {}
    for i in range(0, len(methods)):
        items.append(methods[i](user, keys))
        
    keys['items'] = items
    return render_page(request, constants.TEMPLATE_DASHBOARD, keys)
    
    
def dashboard_dev(request):
    user = get_user(request)
    # TODO: Change this screen to when user is not logged
    if not user:
        return render_page(request, constants.TEMPLATE_DASHBOARD, {'logged': False})
    if constants.DASHBOARD_ITEMS not in request.session:
        items = []
        keys = {}
        config = DashboardConfig.objects.filter(user=user.id)
        if config:
            data = config[0].data
            print data
        else:
            # TODO: Improve this
            dash_model = DashboardConfig()
            dash_model.user = user.id
            dash_model.data = ''
            dash_model.save()
            data = ''
    else:
        keys = request.session[constants.DASHBOARD_ITEMS]
        items = keys['items']
        data = request.GET.get('request_data')
    
    dashconfig = DashboardConfig.objects.get(user=user.id)
    
    all_options = [('all_matches', 'All Matches', get_all_matches), 
                   ('my_requests', 'My Requests', get_my_requests), 
                   ('my_matches', 'My Matches', get_my_matches)]
    
    if data:
        for option in all_options:
            if option[0] in data:
                value = option[2](user,keys)
                if value in items:
                    items.remove(value)
                    dashconfig.data = dashconfig.data.replace(value + ';', '')
                else:
                    items.append(value)
                    if value not in dashconfig.data:
                        dashconfig.data += value + ';'
        
    keys['items'] = items
    keys['dev'] = True
    keys['logged'] = True
    
    dashconfig.save()
    
    options = []
    for option in all_options:
        matching = [s for s in items if option[0] in s]
        if matching:
            options.append((option[1], "request_access('{}')".format(option[0]), 'color:black'))
        else:
            options.append((option[1], "request_access('{}')".format(option[0]), None))
        
    keys['options'] = options
    
    request.session[constants.DASHBOARD_ITEMS] = keys
    request.session[constants.MAINTAIN_STATE] = True
    
    return render_page(request, constants.TEMPLATE_DASHBOARD, keys)

def handler500(request):
    # TODO: Review this to filter only the specific error
    print 'updated local database'
    return sync(request)


def handler404(request):
    return render_page(request, constants.TEMPLATE_ERROR_404)


def sync(request):
    """ :param request: """
    
    all_users = User.objects.using('datatracker').all()
    codestand_users = User.objects.using('default').all().values_list('id', flat=True)
    for us in all_users:
        if us.id not in codestand_users:
            try:
                us.save()
            except:
                pass
    return render_page(request, constants.TEMPLATE_ERROR_500)
