from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from ietf.codematch.matches import views

urlpatterns = patterns('ietf.codematch.matches.views',
    url(r'^show_list/$', views.show_list, name="show_list"),
    url(r'^show_list/(?P<is_my_list>.*)/(?P<att>.*)/(?P<state>.*)$', views.show_list, name="show_list"),
    url(r'^show_list/(?P<is_my_list>.*)/(?P<att>.*)$', views.show_list, name="show_list"),
    url(r'^show_list/(?P<is_my_list>.*)$', views.show_list, name="show_list"),
    url(r'^new/$', views.new , name="new"),
    url(r'^new/(?P<pk>.*)/$', views.new , name="new"),
    url(r'^edit/(?P<pk>[0-9]+)/(?P<ck>[0-9]+)$', views.edit, name="edit"),
    url(r'^remove_link/(?P<ck>[0-9]+)/(?P<link_name>.+)$', views.remove_link, name="remove_link"),
    url(r'^remove_tag/(?P<ck>[0-9]+)/(?P<tag_name>.+)$', views.remove_tag, name="remove_tag"),
    url(r'^remove_document/(?P<pk>[0-9]+)/(?P<doc_name>.+)$', views.remove_document, name="remove_document"),
    url(r'^search/$', views.search, name="search"),
    url(r'^search/(?P<is_my_list>.*)$', views.search, name="search"),
    url(r'^(?P<pk>[0-9]+)/(?P<ck>[0-9]+)$', views.show, name='show'),
)