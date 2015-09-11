from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from ietf.codematch.matches import views

urlpatterns = patterns('ietf.codematch.matches.views',
    url(r'^show_list/$', views.show_list, name="show_list"),
    url(r'^show_my_list/$', views.show_my_list, name="show_my_list"),
    url(r'^new/$', views.new , name="new"),
    url(r'^new/(?P<pk>.*)/$', views.new , name="new"),
    url(r'^edit/(?P<pk>[0-9]+)/(?P<ck>[0-9]+)$', views.edit, name="edit"),
    url(r'^remove_link/(?P<ck>[0-9]+)/(?P<link_name>.+)$', views.remove_link, name="remove_link"),
    url(r'^remove_tag/(?P<ck>[0-9]+)/(?P<tag_name>.+)$', views.remove_tag, name="remove_tag"),
    url(r'^search/$', views.search, name="search"),
    url(r'^(?P<pk>[0-9]+)/(?P<ck>[0-9]+)$', views.show, name='show'),
)
