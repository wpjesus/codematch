from django.conf.urls import patterns, url, include
from ietf.codestand import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name="index"),
                       url(r'^about/$', views.about, name="about"),
                       url(r'^back/$', views.back, name="back"),
                       url(r'^sync/$', views.sync, name="sync"),
                       # Accounts
                       url(r'^accounts/$', include('ietf.codestand.accounts.urls')),

                       # Matches
                       url(r'^matches/$', include('ietf.codestand.matches.urls')),

                       # Requests
                       url(r'^requests/$', include('ietf.codestand.requests.urls')),

                       )
