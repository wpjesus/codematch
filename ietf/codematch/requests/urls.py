from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from ietf.codematch.requests import views

urlpatterns = patterns('ietf.codematch.requests.views',
    url(r'^show_list/$', views.show_list, name="show_list"),
    url(r'^show_mentoring_list/$', views.show_mentoring_list, name="show_mentoring_list"),
    url(r'^show_my_list/$', views.show_my_list, name="show_my_list"),
    url(r'^new/$', views.new , name="new"),
    url(r'^edit/(?P<pk>[0-9]+)$', views.edit, name="edit"),
    url(r'^search/$', views.search, name="search"),
    url(r'^(?P<pk>[0-9]+)/$', views.show, name='show'),
)
