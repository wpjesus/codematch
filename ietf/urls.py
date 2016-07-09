# Copyright The IETF Trust 2007, 2009, All Rights Reserved

from django.conf import settings
from django.conf.urls import patterns, include
from django.contrib import admin
from django.views.generic import TemplateView

from ietf.liaisons.sitemaps import LiaisonMap
from ietf.ipr.sitemaps import IPRMap
from ietf import api

import debug_toolbar

admin.autodiscover()
api.autodiscover()

# sometimes, this code gets called more than once, which is an
# that seems impossible to work around.
try:
    admin.site.disable_action('delete_selected')
except KeyError:
    pass

sitemaps = {
    'liaison': LiaisonMap,
    'ipr': IPRMap,
}

urlpatterns = patterns('',
    (r'^$', 'ietf.doc.views_search.frontpage'),
    (r'^accounts/', include('ietf.ietfauth.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^ann/', include('ietf.nomcom.redirect_ann_urls')),
    (r'^community/', include('ietf.community.urls')),
    (r'^accounts/settings/', include('ietf.cookies.urls')),
    (r'^doc/', include('ietf.doc.urls')),
    (r'^drafts/', include('ietf.doc.redirect_drafts_urls')),
    (r'^mailtrigger/',include('ietf.mailtrigger.urls')),
    (r'^feed/', include('ietf.feed_urls')),
    (r'^group/', include('ietf.group.urls')),
    (r'^help/', include('ietf.help.urls')),
    (r'^idtracker/', include('ietf.doc.redirect_idtracker_urls')),
    (r'^iesg/', include('ietf.iesg.urls')),
    (r'^ipr/', include('ietf.ipr.urls')),
    (r'^liaison/', include('ietf.liaisons.urls')),
    (r'^list/', include('ietf.mailinglists.urls')),
    (r'^meeting/', include('ietf.meeting.urls')),
    (r'^nomcom/', include('ietf.nomcom.urls')),
    (r'^person/', include('ietf.person.urls')),
    (r'^release/', include('ietf.release.urls')),
    (r'^secr/', include('ietf.secr.urls')),
    (r'^sitemap-(?P<section>.+).xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.index', { 'sitemaps': sitemaps}),
    (r'^submit/', include('ietf.submit.urls')),
    (r'^sync/', include('ietf.sync.urls')),
    (r'^stream/', include('ietf.group.urls_stream')),
    (r'^templates/', include('ietf.dbtemplate.urls')),
    (r'^(?P<group_type>(wg|rg|ag|team|dir|area))/', include('ietf.group.urls_info')),

    # Redirects
    (r'^(?P<path>public)/', include('ietf.redirects.urls')),

    # Google webmaster tools verification url
    (r'^googlea30ad1dacffb5e5b.html', TemplateView.as_view(template_name='googlea30ad1dacffb5e5b.html')),
)

if settings.IS_CODEMATCH_APP:
    urlpatterns += patterns('',
    (r'^codematch/', include('ietf.codematch.urls')),
    (r'^codematch/matches/', include('ietf.codematch.matches.urls')),
    (r'^codematch/requests/', include('ietf.codematch.requests.urls')),
    (r'^codematch/accounts/', include('ietf.codematch.accounts.urls')),
)
if settings.DEBUG:
    urlpatterns += patterns('',
    (r'^codematch/__debug__/', include(debug_toolbar.urls)),
)


# Endpoints for Tastypie's REST API
urlpatterns += patterns('',
    (r'^api/v1/?$', api.top_level),
)
for n,a in api._api_list:
    urlpatterns += patterns('',
        (r'^api/v1/', include(a.urls)),
    )

# This is needed to serve files during testing
#if settings.SERVER_MODE in ('development', 'test'):
#    urlpatterns += ( staticfiles_urlpatterns()
#        + patterns('',
#            (r'^_test500/$', lambda x: None),
#            (r'^environment/$', 'ietf.help.views.environment'),
#            ## maybe preserve some static legacy URLs ?
#            (r'^(?P<path>(?:images|css|js)/.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT+'ietf/'}),
#        )
#    )

# This is needed to serve files which are not handled by collectstatic :
if settings.SERVER_MODE in ('development', 'test'):
     urlpatterns += patterns('',
         (r'^(?P<path>(?:images|css|js|test|static|fonts|other)/.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
         # (r'^(?P<path>autocomplete/(?:img|css|js)/.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
         (r'^(?P<path>admin/(?:img|css|js)/.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
         (r'^(?P<path>secretariat/(img|css|js)/.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
         (r'^(?P<path>robots\.txt)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT+"dev/"}),
         (r'^_test500/$', lambda x: None),
         (r'^environment/$', 'ietf.help.views.environment'),
)
