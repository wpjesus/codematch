from django.conf.urls import patterns, url, include
from ietf.codematch import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name="index"),
                       url(r'^about/$', views.about, name="about"),
                       url(r'^back/$', views.back, name="back"),
                       url('personcomplete/$', views.PersonAutocomplete.as_view(), name='personcomplete'),
                       # Accounts
                       url(r'^accounts/$', include('ietf.codematch.accounts.urls')),

                       # Matches
                       url(r'^matches/$', include('ietf.codematch.matches.urls')),

                       # Requests
                       url(r'^requests/$', include('ietf.codematch.requests.urls')),

                       )
