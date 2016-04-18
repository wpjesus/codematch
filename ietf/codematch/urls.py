from django.conf.urls import *
from ietf.codematch import views

handler500 = 'ietf.codematch.views.handler500'

urlpatterns = patterns('',
                       url(r'^$', views.index, name="index"),
                       url(r'^about/$', views.about, name="about"),
                       url(r'^back/$', views.back, name="back"),
                       url(r'^sync/$', views.sync, name="sync"),
                       # Accounts
                       url(r'^accounts/$', include('ietf.codematch.accounts.urls')),

                       # Matches
                       url(r'^matches/$', include('ietf.codematch.matches.urls')),

                       # Requests
                       url(r'^requests/$', include('ietf.codematch.requests.urls')),

                       )
