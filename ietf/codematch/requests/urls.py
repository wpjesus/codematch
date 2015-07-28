from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from ietf.codematch.requests import views

urlpatterns = patterns('ietf.codematch.requests.views',
    url(r'^showlist/$', views.showlist, name="showlist"),
    url(r'^new/$', views.new , name="new"),
    url(r'^search/$', views.search, name="search"),
    url(r'^(?P<pk>[0-9]+)/$', views.show, name='show'),
)
