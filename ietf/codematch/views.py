from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from ietf.codematch.helpers.utils import (render_page, get_user)
from ietf.codematch import constants
from ietf.codematch.dashboard import (get_all_matches, get_my_matches, get_my_requests)
from ietf.codematch.matches.models import DashboardConfig

def index(request):
    return render_page(request, constants.TEMPLATE_INDEX)


def about(request):
    return render_page(request, constants.TEMPLATE_ABOUT)


def request_access(request):
    print "DJANGO VIEW"
    
    
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
    # TODO: Trocar tela quando usuario nao cadastrado
    if not user:
        return render_page(request, constants.TEMPLATE_DASHBOARD, {'logged': False})
    if not constants.DASHBOARD_ITEMS in request.session:
        items = []
        keys = {}
        config = DashboardConfig.objects.filter(user=user.id)
        if config:
            data = config[0].data
            print data
        else:
            dashModel = DashboardConfig()
            dashModel.user = user.id
            dashModel.data = ''
            dashModel.save()
            data = ''
    else:
        keys = request.session[constants.DASHBOARD_ITEMS]
        items = keys['items']
        data = request.GET.get('request_data')
    
    dashconfig = DashboardConfig.objects.get(user=user.id)
    
    if data:
        if 'all_matches' in data:
            all_matches = get_all_matches(user, keys)
            if all_matches in items:
                items.remove(all_matches)
                dashconfig.data = dashconfig.data.replace(all_matches + ';', '')
            else:
                items.append(all_matches)
                if all_matches not in dashconfig.data:
                    dashconfig.data += all_matches + ';'
        if 'my_requests' in data:
            my_requests = get_my_requests(user, keys)
            if my_requests in items:
                items.remove(my_requests)
                dashconfig.data = dashconfig.data.replace(my_requests + ';', '')
            else:
                items.append(my_requests)
                if my_requests not in dashconfig.data:
                    dashconfig.data += my_requests + ';'
        if 'my_matches' in data:
            my_matches = get_my_matches(user, keys)
            if my_matches in items:
                items.remove(my_matches)
                dashconfig.data = dashconfig.data.replace(my_matches + ';', '')
            else:
                items.append(my_matches)
                if my_matches not in dashconfig.data:
                    dashconfig.data += my_matches + ';'
        
    keys['items'] = items
    keys['dev'] = True
    keys['logged'] = True
    
    dashconfig.save()
    
    request.session[constants.DASHBOARD_ITEMS] = keys
    request.session[constants.MAINTAIN_STATE] = True
    
    return render_page(request, constants.TEMPLATE_DASHBOARD, keys)


def back(request):
    template = "/codematch/"

    if "previous_template" in request.session:
        template = request.session["previous_template"]

    return HttpResponseRedirect(template)


def handler500(request):
    #TODO: Rever para filtrar apenas o erro especifico 500
    sync(request)
    print 'updated local database'
    #  return render_page(request, constants.TEMPLATE_ERROR_500)
    return render_page(request, constants.TEMPLATE_INDEX)


def handler404(request):
    return render_page(request, constants.TEMPLATE_ERROR_404)


def sync(request):    
    """all_persons = Person.objects.using('datatracker')
    codematch_persons = Person.objects.using('default').all().values_list('id', flat=True)
    
    for person in all_persons:
        if person.id not in codematch_persons:
            try:
                person.save()
            except:
                pass"""
    all_users = User.objects.using('datatracker').all()
    codematch_users = User.objects.using('default').all().values_list('id', flat=True)
    for us in all_users:
        if us.id not in codematch_users:
            try:
                us.save()
            except:
                pass
