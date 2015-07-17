from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from ietf.codematch import views

urlpatterns = patterns('',
    url(r'^$', views.index, name="index"),
                       
    #Matches
    url(r'^matches/$', include('ietf.codematch.matches.urls')),
    
    #Requests
    #url(r'^requests/$', include('ietf.codematch.requests.urls')),
)
