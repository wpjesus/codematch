from django.conf.urls import patterns, url
from ietf.codematch.requests import views

urlpatterns = patterns('ietf.codematch.requests.views',
                       url(r'^show_list/$', views.show_list, name="show_list"),
                       url(r'^show_list/(?P<type_list>.*)/(?P<att>.*)/(?P<state>.*)$', views.show_list,
                           name="show_list"),
                       url(r'^show_list/(?P<type_list>.*)/(?P<att>.*)$', views.show_list, name="show_list"),
                       url(r'^show_list/(?P<type_list>.*)$', views.show_list, name="show_list"),
                       url(r'^new/$', views.new, name="new"),
                       url(r'^edit/(?P<pk>[0-9]+)$', views.edit, name="edit"),
                       url(r'^remove_contact/(?P<pk>[0-9]+)/(?P<contact_name>.+)$', views.remove_contact,
                           name="remove_contact"),
                       url(r'^remove_document/(?P<pk>[0-9]+)/(?P<doc_name>.+)$', views.remove_document,
                           name="remove_document"),
                       url(r'^remove_tag/(?P<pk>[0-9]+)/(?P<tag_name>.+)$', views.remove_tag, name="remove_tag"),
                       url(r'^search/$', views.search, name="search"),
                       url(r'^search/(?P<type_list>.*)$', views.search, name="search"),
                       url(r'^(?P<pk>[0-9]+)/$', views.show, name='show'),
                       )
