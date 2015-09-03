from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from ietf.codematch.requests import views

urlpatterns = patterns('ietf.codematch.requests.views',
    url(r'^show_list/$', views.show_list, name="show_list"),
    url(r'^show_mentoring_list/$', views.show_mentoring_list, name="show_mentoring_list"),
    url(r'^show_my_list/$', views.show_my_list, name="show_my_list"),
    url(r'^new/$', views.new , name="new"),
    url(r'^update/(?P<pk>[0-9]+)$', views.update, name="update"),
    url(r'^remove_document/(?P<pk>[0-9]+)/(?P<doc_name>.+)$', views.remove_document, name="remove_document"),
    url(r'^remove_tag/(?P<pk>[0-9]+)/(?P<tag_name>.+)$', views.remove_tag, name="remove_tag"),
    url(r'^search/$', views.search, name="search"),
    url(r'^(?P<pk>[0-9]+)/$', views.show, name='show'),
)
