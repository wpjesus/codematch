from django.conf.urls import patterns, url, include
from django.contrib.auth.views import login, logout

urlpatterns = patterns('ietf.codestand.accounts.views',
                       url(r'^$', 'index', name='index'),
                       url(r'^login/$', login, {'template_name': 'codestand/accounts/login.html'}),
                       url(r'^logout/$', logout, {'template_name': 'codestand/index.html'}),
                       url(r'^register/$', 'register', name='register'),
                       url(r'^profile/$', 'profile', name='profile'),
                       url(r'^top_coders/$', 'top_coders', name='top_coders'),
                       )
