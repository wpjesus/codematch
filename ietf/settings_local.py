DATABASES = {
    'default': {
        'NAME': 'ietf_utf8',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'matheuspfitscher',
        'PASSWORD': 'ietf',
        'HOST': '127.0.0.1'
    },
    #'datatracker': {
    #    'NAME': 'ietf_utf8',
    #    'ENGINE': 'django.db.backends.mysql',
    #    'USER': 'matheuspfitscher',
    #    'PASSWORD': 'ietf', # Contact henrik@levkowetz.com to get the password
    #    'HOST': '127.0.0.1'
    #},
    'datatracker': {
        'NAME': 'ietf_utf8',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'django_readonly',
        'PASSWORD': 'f$xdv#vzwi',
        'HOST': 'zinfandel.tools.ietf.org',
    }
    #'datatracker': {
    #    'NAME': 'ietf_utf8',
    #    'ENGINE': 'django.db.backends.mysql',
    #    'USER': 'codematch',
    #    'PASSWORD': 'codematcher',
    #    'HOST': 'ietf.org',
    #}
}

DATABASE_ROUTERS = ["ietf.new_router.DatatrackerRouter"]

# Since the zinfandel database above is read-only, you also need to have a
# different session backend in order to avoid exceptions due to attempts
# to save session data to the readonly database:
# NOTE: you should omit this if you are using a local database
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# Since the grenache database above is remote, you probably also should
# use a fast local cache (this requires you to set up memcached.  Alternatively,
# you could use a disk cache.
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

DEBUG_TOOLBAR_PATCH_SETTINGS = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# If you are using a remote database, you may want to enable memcached instead:
# CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': '127.0.0.1:11211',
#    }
# }

SERVER_MODE	  = 'development'
DEBUG             = True

# If you need to debug email, you can start a debugging server that just
# outputs whatever it receives with:
#   python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None

# Depending upon what cases you work on, the
# server may need to store files locally.  Configuration is
# required to specify the location.  
# You should create the subdirectories if they don't already exist.
# You can get a local copy of idnits using the download link at
# http://tools.ietf.org/tools/idnits/

ARCHIVE_PATH = '<local path to where you want to keep the files below>'
INTERNET_DRAFT_PATH = '%s/devsync/ietf-ftp/internet-drafts' % ARCHIVE_PATH
INTERNET_DRAFT_ARCHIVE_DIR = INTERNET_DRAFT_PATH
IDSUBMIT_REPOSITORY_PATH = INTERNET_DRAFT_PATH
RFC_PATH = '%s/devsync/ietf-ftp/rfc/' % ARCHIVE_PATH
IESG_WG_EVALUATION_DIR = '%s/devsync/www6/iesg/evaluation' % ARCHIVE_PATH
IETFWG_DESCRIPTIONS_PATH = '%s/devsync/www6s/wg-descriptions'  % ARCHIVE_PATH
IPR_DOCUMENT_PATH = '%s/devsync/ietf-ftp/ietf/IPR' % ARCHIVE_PATH
AGENDA_PATH = '%s/devsync/www6s/proceedings' % ARCHIVE_PATH
AGENDA_PATH_PATTERN = AGENDA_PATH + '/%(meeting)s/agenda/%(wg)s.%(ext)s'
CHARTER_PATH = '%s/devsync/ietf-ftp/charter/' % ARCHIVE_PATH
STATUS_CHANGE_PATH = '%s/devsync/ietf-ftp/status-changes/' % ARCHIVE_PATH
CONFLICT_REVIEW_PATH = '%s/devsync/ietf-ftp/conflict-reviews' % ARCHIVE_PATH
NOMCOM_PUBLIC_KEYS_DIR = '%s/nomcom_keys/public_keys' % ARCHIVE_PATH
IDSUBMIT_IDNITS_BINARY = '<path to a local copy of idnits>'

""" Codematch Settings """

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

# If any folder structure on Apache 
#(eg. codematch-dev - CODEMATCH_PREFIX="/codematch-dev/")
CODEMATCH_PREFIX = ""
#(eg. codematch-dev - STATIC_URL="/static/") 
STATIC_URL = "/static/"

IS_CODEMATCH_APP = True

#Application that must be installed by Codematch
CODEMATCH_APPS = (
        'ietf.codematch',
        'ietf.codematch.accounts',
        'ietf.codematch.matches',
        'ietf.codematch.requests',
    )
if DEBUG:
    CODEMATCH_APPS += ('debug_toolbar',)

