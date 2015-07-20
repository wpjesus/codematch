from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from ietf.codematch.matches import views

urlpatterns = patterns('ietf.codematch.matches.views',
    url(r'^$', views.index, name="index"),
    url(r'^showlist/$', views.showlist, name="showlist"),
    url(r'^about/$', views.about , name="about"),
    url(r'^new/$', views.new , name="new"),
    url(r'^search/$', views.search, name="search"),
    url(r'^(?P<pk>[0-9]+)/$', views.show, name='show'),
)
