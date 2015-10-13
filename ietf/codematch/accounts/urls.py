from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from django.contrib.auth.views import login, logout

from ietf.codematch import views

urlpatterns = patterns('ietf.codematch.accounts.views',
    url(r'^$', 'index', name='index'),
    url(r'^login/$', login, {'template_name': 'codematch/accounts/login.html'}),
    url(r'^logout/$', logout, {'template_name': 'codematch/index.html'}),
    url(r'^register/$', 'register', name='register'),
    url(r'^profile/$', 'profile', name='profile'),
    url(r'^top_coders/$', 'top_coders', name='top_coders'),
)
