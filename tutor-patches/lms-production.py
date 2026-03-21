# -*- coding: utf-8 -*-
import os
from lms.envs.production import *

####### Settings common to LMS and CMS
import json
import os

from xmodule.modulestore.modulestore_settings import update_module_store_settings

# Mongodb connection parameters: simply modify `mongodb_parameters` to affect all connections to MongoDb.
mongodb_parameters = {
    "db": "openedx",
    "host": "mongodb",
    "port": 27017,
    "user": None,
    "password": None,
    # Connection/Authentication
    "connect": False,
    "ssl": False,
    "authsource": "admin",
    "replicaSet": None,
    
}
DOC_STORE_CONFIG = mongodb_parameters
CONTENTSTORE = {
    "ENGINE": "xmodule.contentstore.mongo.MongoContentStore",
    "ADDITIONAL_OPTIONS": {},
    "DOC_STORE_CONFIG": DOC_STORE_CONFIG
}
# Load module store settings from config files
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)
DATA_DIR = "/openedx/data/modulestore"

for store in MODULESTORE["default"]["OPTIONS"]["stores"]:
   store["OPTIONS"]["fs_root"] = DATA_DIR

# Behave like memcache when it comes to connection errors
DJANGO_REDIS_IGNORE_EXCEPTIONS = True

# Meilisearch connection parameters
MEILISEARCH_ENABLED = True
MEILISEARCH_URL = "http://meilisearch:7700"
MEILISEARCH_PUBLIC_URL = "https://meilisearch.academie.staging.missionformations.com"
MEILISEARCH_INDEX_PREFIX = "tutor_"
MEILISEARCH_API_KEY = os.environ.get("MEILISEARCH_API_KEY", "")
MEILISEARCH_MASTER_KEY = os.environ.get("MEILISEARCH_MASTER_KEY", "")
SEARCH_ENGINE = "search.meilisearch.MeilisearchEngine"

# Common cache config
CACHES = {
    "default": {
        "KEY_PREFIX": "default",
        "VERSION": "1",
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    },
    "general": {
        "KEY_PREFIX": "general",
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    },
    "mongo_metadata_inheritance": {
        "KEY_PREFIX": "mongo_metadata_inheritance",
        "TIMEOUT": 300,
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    },
    "configuration": {
        "KEY_PREFIX": "configuration",
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    },
    "celery": {
        "KEY_PREFIX": "celery",
        "TIMEOUT": 7200,
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    },
    "course_structure_cache": {
        "KEY_PREFIX": "course_structure",
        "TIMEOUT": 604800, # 1 week
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    },
    "ora2-storage": {
        "KEY_PREFIX": "ora2-storage",
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    }
}

# The default Django contrib site is the one associated to the LMS domain name. 1 is
# usually "example.com", so it's the next available integer.
SITE_ID = 2

# Contact addresses
CONTACT_MAILING_ADDRESS = "Mission Formations - Staging - https://academie.staging.missionformations.com"
DEFAULT_FROM_EMAIL = ENV_TOKENS.get("DEFAULT_FROM_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
DEFAULT_FEEDBACK_EMAIL = ENV_TOKENS.get("DEFAULT_FEEDBACK_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
SERVER_EMAIL = ENV_TOKENS.get("SERVER_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
TECH_SUPPORT_EMAIL = ENV_TOKENS.get("TECH_SUPPORT_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
CONTACT_EMAIL = ENV_TOKENS.get("CONTACT_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
BUGS_EMAIL = ENV_TOKENS.get("BUGS_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
UNIVERSITY_EMAIL = ENV_TOKENS.get("UNIVERSITY_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
PRESS_EMAIL = ENV_TOKENS.get("PRESS_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
PAYMENT_SUPPORT_EMAIL = ENV_TOKENS.get("PAYMENT_SUPPORT_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
BULK_EMAIL_DEFAULT_FROM_EMAIL = ENV_TOKENS.get("BULK_EMAIL_DEFAULT_FROM_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
API_ACCESS_MANAGER_EMAIL = ENV_TOKENS.get("API_ACCESS_MANAGER_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
API_ACCESS_FROM_EMAIL = ENV_TOKENS.get("API_ACCESS_FROM_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])

# Get rid completely of coursewarehistoryextended, as we do not use the CSMH database
INSTALLED_APPS.remove("lms.djangoapps.coursewarehistoryextended")
DATABASE_ROUTERS.remove(
    "openedx.core.lib.django_courseware_routers.StudentModuleHistoryExtendedRouter"
)

# Set uploaded media file path
MEDIA_ROOT = "/openedx/media/"

# Video settings
VIDEO_IMAGE_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT
VIDEO_TRANSCRIPTS_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT

GRADES_DOWNLOAD = {
    "STORAGE_TYPE": "",
    "STORAGE_KWARGS": {
        "base_url": "/media/grades/",
        "location": "/openedx/media/grades",
    },
}

# ORA2
ORA2_FILEUPLOAD_BACKEND = "filesystem"
ORA2_FILEUPLOAD_ROOT = "/openedx/data/ora2"
FILE_UPLOAD_STORAGE_BUCKET_NAME = "openedxuploads"
ORA2_FILEUPLOAD_CACHE_NAME = "ora2-storage"

# Change syslog-based loggers which don't work inside docker containers
LOGGING["handlers"]["local"] = {
    "class": "logging.handlers.WatchedFileHandler",
    "filename": os.path.join(LOG_DIR, "all.log"),
    "formatter": "standard",
}
LOGGING["handlers"]["tracking"] = {
    "level": "DEBUG",
    "class": "logging.handlers.WatchedFileHandler",
    "filename": os.path.join(LOG_DIR, "tracking.log"),
    "formatter": "standard",
}
LOGGING["loggers"]["tracking"]["handlers"] = ["console", "local", "tracking"]

# Silence some loggers (note: we must attempt to get rid of these when upgrading from one release to the next)
LOGGING["loggers"]["blockstore.apps.bundles.storage"] = {"handlers": ["console"], "level": "WARNING"}

# These warnings are visible in simple commands and init tasks
import warnings

# REMOVE-AFTER-V20: check if we can remove these lines after upgrade.
try:
    from django.utils.deprecation import RemovedInDjango50Warning, RemovedInDjango51Warning
    # RemovedInDjango5xWarning: 'xxx' is deprecated. Use 'yyy' in 'zzz' instead.
    warnings.filterwarnings("ignore", category=RemovedInDjango50Warning)
    warnings.filterwarnings("ignore", category=RemovedInDjango51Warning)
    # DeprecationWarning: 'imghdr' is deprecated and slated for removal in Python 3.13
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="pgpy.constants")
except ImportError:
    pass # If the warnings don't exist we don't need to filter them.
    
# Email
EMAIL_USE_SSL = False
# Forward all emails from edX's Automated Communication Engine (ACE) to django.
ACE_ENABLED_CHANNELS = ["django_email"]
ACE_CHANNEL_DEFAULT_EMAIL = "django_email"
ACE_CHANNEL_TRANSACTIONAL_EMAIL = "django_email"
EMAIL_FILE_PATH = "/tmp/openedx/emails"

# Language/locales
LANGUAGE_COOKIE_NAME = "openedx-language-preference"

# Allow the platform to include itself in an iframe
X_FRAME_OPTIONS = "SAMEORIGIN"


JWT_AUTH["JWT_ISSUER"] = "https://academie.staging.missionformations.com/oauth2"
JWT_AUTH["JWT_AUDIENCE"] = "openedx"
_JWT_SECRET = os.environ.get("JWT_SECRET_KEY", "")
JWT_AUTH["JWT_SECRET_KEY"] = _JWT_SECRET
JWT_AUTH["JWT_PRIVATE_SIGNING_JWK"] = json.dumps(
    {
        "kid": os.environ.get("JWT_RSA_KID", "openedx"),
        "kty": "RSA",
        "e": os.environ.get("JWT_RSA_E", "AQAB"),
        "d": os.environ.get("JWT_RSA_D", ""),
        "n": os.environ.get("JWT_RSA_N", ""),
        "p": os.environ.get("JWT_RSA_P", ""),
        "q": os.environ.get("JWT_RSA_Q", ""),
        "dq": os.environ.get("JWT_RSA_DQ", ""),
        "dp": os.environ.get("JWT_RSA_DP", ""),
        "qi": os.environ.get("JWT_RSA_QI", ""),
    }
)
JWT_AUTH["JWT_PUBLIC_SIGNING_JWK_SET"] = json.dumps(
    {
        "keys": [
            {
                "kid": os.environ.get("JWT_RSA_KID", "openedx"),
                "kty": "RSA",
                "e": os.environ.get("JWT_RSA_E", "AQAB"),
                "n": os.environ.get("JWT_RSA_N", ""),
            }
        ]
    }
)
JWT_AUTH["JWT_ISSUERS"] = [
    {
        "ISSUER": "https://academie.staging.missionformations.com/oauth2",
        "AUDIENCE": "openedx",
        "SECRET_KEY": _JWT_SECRET
    }
]

# Enable/Disable some features globally
FEATURES["ENABLE_DISCUSSION_SERVICE"] = False
FEATURES["PREVENT_CONCURRENT_LOGINS"] = False
FEATURES["ENABLE_CORS_HEADERS"] = True

# CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_INSECURE = False
# Note: CORS_ALLOW_HEADERS is intentionally not defined here, because it should
# be consistent across deployments, and is therefore set in edx-platform.

# Add your MFE and third-party app domains here
CORS_ORIGIN_WHITELIST = []

# Disable codejail support
# explicitely configuring python is necessary to prevent unsafe calls
import codejail.jail_code
codejail.jail_code.configure("python", "nonexistingpythonbinary", user=None)
# another configuration entry is required to override prod/dev settings
CODE_JAIL = {
    "python_bin": "nonexistingpythonbinary",
    "user": None,
}

OPENEDX_LEARNING = {
    'MEDIA': {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": "/openedx/media-private/openedx-learning",
        }
    }
}

# edx-event-bus-redis settings
EVENT_BUS_PRODUCER = 'edx_event_bus_redis.create_producer'
EVENT_BUS_REDIS_CONNECTION_URL = 'redis://@redis:6379/'
EVENT_BUS_TOPIC_PREFIX = 'dev'
EVENT_BUS_CONSUMER = 'edx_event_bus_redis.RedisEventConsumer'


######## End of settings common to LMS and CMS

######## Common LMS settings
LOGIN_REDIRECT_WHITELIST = ["studio.staging.missionformations.com"]

# Better layout of honor code/tos links during registration
REGISTRATION_EXTRA_FIELDS["terms_of_service"] = "hidden"
REGISTRATION_EXTRA_FIELDS["honor_code"] = "hidden"

# Fix media files paths
PROFILE_IMAGE_BACKEND["options"]["location"] = os.path.join(
    MEDIA_ROOT, "profile-images/"
)

COURSE_CATALOG_VISIBILITY_PERMISSION = "see_in_catalog"
COURSE_ABOUT_VISIBILITY_PERMISSION = "see_about_page"

# Allow insecure oauth2 for local interaction with local containers
OAUTH_ENFORCE_SECURE = False

# Email settings
DEFAULT_EMAIL_LOGO_URL = LMS_ROOT_URL + "/theming/asset/images/logo.png"
BULK_EMAIL_SEND_USING_EDX_ACE = True
FEATURES["ENABLE_FOOTER_MOBILE_APP_LINKS"] = False

# Branding
MOBILE_STORE_ACE_URLS = {}
SOCIAL_MEDIA_FOOTER_ACE_URLS = {}

# Make it possible to hide courses by default from the studio
SEARCH_SKIP_SHOW_IN_CATALOG_FILTERING = False

# Caching
CACHES["staticfiles"] = {
    "KEY_PREFIX": "staticfiles_lms",
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    "LOCATION": "staticfiles_lms",
}

# Enable search features
FEATURES["ENABLE_COURSE_DISCOVERY"] = True
FEATURES["ENABLE_COURSEWARE_SEARCH"] = True
FEATURES["ENABLE_DASHBOARD_SEARCH"] = True

# Create folders if necessary
for folder in [DATA_DIR, LOG_DIR, MEDIA_ROOT, STATIC_ROOT, ORA2_FILEUPLOAD_ROOT]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

# MFE: enable API and set a low cache timeout for the settings. otherwise, weird
# configuration bugs occur. Also, the view is not costly at all, and it's also cached on
# the frontend. (5 minutes, hardcoded)
ENABLE_MFE_CONFIG_API = True
MFE_CONFIG_API_CACHE_TIMEOUT = 1

# MFE-specific settings


FEATURES['ENABLE_NEW_BULK_EMAIL_EXPERIENCE'] = True


# mission_central_admin plugin settings
MISSION_FORMATIONS_FORMATEURS_FORMATIONS = {'formateur1@example.com': ['formation-python', 'formation-excel'], 'formateur2@example.com': ['formation-rse', 'formation-management'], 'admin@missionformations.com': 'ALL'}
MISSION_CENTRAL_ADMIN_ALLOWED = ['admin@missionformations.com', 'superadmin.mission.test@missionformations.local']

import importlib.util
if importlib.util.find_spec('lms.djangoapps.mission_central_admin'):
    if 'lms.djangoapps.mission_central_admin' not in INSTALLED_APPS:
        INSTALLED_APPS.append('lms.djangoapps.mission_central_admin')
# mission_certificates_policy: sidebar menu includes only obtained certificates
MF_CERTIFICATES_MENU_ONLY_OBTAINED = True

# Certificats HTML — activer le rendu web des certificats Mission Formations
FEATURES['CERTIFICATES_HTML_VIEW'] = True

# Permettre les templates de certificats personnalises (theme ou DB)
FEATURES['CUSTOM_CERTIFICATE_TEMPLATES_ENABLED'] = True
# mission_theme_lock: enforce Mission themed auth stack
DEFAULT_SITE_THEME = "mission-theme"
FEATURES['ENABLE_AUTHN_MICROFRONTEND'] = False
FEATURES['ENABLE_THIRD_PARTY_AUTH'] = False
FEATURES['ENABLE_COMBINED_LOGIN_REGISTRATION'] = True
ENABLE_LEARNER_HOME_MFE = False
LEARNER_HOME_MFE_REDIRECT_PERCENTAGE = 0

if "/openedx/themes" not in COMPREHENSIVE_THEME_DIRS:
    COMPREHENSIVE_THEME_DIRS.append("/openedx/themes")
if "/openedx/themes/mission-theme/lms/static" not in STATICFILES_DIRS:
    STATICFILES_DIRS.append("/openedx/themes/mission-theme/lms/static")
# mission_braze_enrollment: native Open edX enrollment confirmation email via Braze
EDX_BRAZE_API_KEY = ""
EDX_BRAZE_API_SERVER = ""
BRAZE_COURSE_ENROLLMENT_CANVAS_ID = ""

######## End of common LMS settings

ALLOWED_HOSTS = [
    ENV_TOKENS.get("LMS_BASE"),
    "lms",
]
CORS_ORIGIN_WHITELIST.append("https://academie.staging.missionformations.com")


# Properly set the "secure" attribute on session/csrf cookies. This is required in
# Chrome to support samesite=none cookies.
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"


# CMS authentication
IDA_LOGOUT_URI_LIST.append("https://studio.staging.missionformations.com/logout/")

# Required to display all courses on start page
SEARCH_SKIP_ENROLLMENT_START_DATE_FILTERING = True

# Dynamic config API settings
# https://openedx.github.io/frontend-platform/module-Config.html
MFE_CONFIG = {
    "BASE_URL": "apps.academie.staging.missionformations.com",
    "CSRF_TOKEN_API_PATH": "/csrf/api/v1/token",
    "CREDENTIALS_BASE_URL": "",
    "DISCOVERY_API_BASE_URL": "",
    "FAVICON_URL": "https://academie.staging.missionformations.com/favicon.ico",
    "INFO_EMAIL": "chabanezakia@gmail.com",
    "LANGUAGE_PREFERENCE_COOKIE_NAME": "openedx-language-preference",
    "LMS_BASE_URL": "https://academie.staging.missionformations.com",
    "LOGIN_URL": "https://academie.staging.missionformations.com/login",
    "LOGO_URL": "https://academie.staging.missionformations.com/theming/asset/images/logo.png",
    "LOGO_WHITE_URL": "https://academie.staging.missionformations.com/theming/asset/images/logo.png",
    "LOGO_TRADEMARK_URL": "https://academie.staging.missionformations.com/theming/asset/images/logo.png",
    "LOGOUT_URL": "https://academie.staging.missionformations.com/logout",
    "MARKETING_SITE_BASE_URL": "https://academie.staging.missionformations.com",
    "PASSWORD_RESET_SUPPORT_LINK": "mailto:chabanezakia@gmail.com",
    "REFRESH_ACCESS_TOKEN_ENDPOINT": "https://academie.staging.missionformations.com/login_refresh",
    "SITE_NAME": "Mission Formations - Staging",
    "STUDIO_BASE_URL": "https://studio.staging.missionformations.com",
    "USER_INFO_COOKIE_NAME": "user-info",
    "ACCESS_TOKEN_COOKIE_NAME": "edx-jwt-cookie-header-payload",
}

# MFE-specific settings




ACCOUNT_MICROFRONTEND_URL = "https://apps.academie.staging.missionformations.com/account/"
MFE_CONFIG["ACCOUNT_SETTINGS_URL"] = ACCOUNT_MICROFRONTEND_URL



MFE_CONFIG["COURSE_AUTHORING_MICROFRONTEND_URL"] = "https://apps.academie.staging.missionformations.com/authoring"
MFE_CONFIG["ENABLE_ASSETS_PAGE"] = "true"
MFE_CONFIG["ENABLE_HOME_PAGE_COURSE_API_V2"] = "true"
MFE_CONFIG["ENABLE_PROGRESS_GRAPH_SETTINGS"] = "true"
MFE_CONFIG["ENABLE_TAGGING_TAXONOMY_PAGES"] = "true"
MFE_CONFIG["ENABLE_UNIT_PAGE"] = "true"
MFE_CONFIG["MEILISEARCH_ENABLED"] = "true"



DISCUSSIONS_MICROFRONTEND_URL = "https://apps.academie.staging.missionformations.com/discussions"
MFE_CONFIG["DISCUSSIONS_MFE_BASE_URL"] = DISCUSSIONS_MICROFRONTEND_URL
DISCUSSIONS_MFE_FEEDBACK_URL = None



WRITABLE_GRADEBOOK_URL = "https://apps.academie.staging.missionformations.com/gradebook"





LEARNING_MICROFRONTEND_URL = "https://apps.academie.staging.missionformations.com/learning"
MFE_CONFIG["LEARNING_BASE_URL"] = "https://apps.academie.staging.missionformations.com/learning"



ORA_GRADING_MICROFRONTEND_URL = "https://apps.academie.staging.missionformations.com/ora-grading"



PROFILE_MICROFRONTEND_URL = "https://apps.academie.staging.missionformations.com/profile/u/"
MFE_CONFIG["ACCOUNT_PROFILE_URL"] = "https://apps.academie.staging.missionformations.com/profile"



COMMUNICATIONS_MICROFRONTEND_URL = "https://apps.academie.staging.missionformations.com/communications"
MFE_CONFIG["SCHEDULE_EMAIL_SECTION"] = True



ADMIN_CONSOLE_MICROFRONTEND_URL = "https://apps.academie.staging.missionformations.com/admin-console"
MFE_CONFIG["ADMIN_CONSOLE_URL"] = ADMIN_CONSOLE_MICROFRONTEND_URL


LOGIN_REDIRECT_WHITELIST.append("apps.academie.staging.missionformations.com")
CORS_ORIGIN_WHITELIST.append("https://apps.academie.staging.missionformations.com")
CSRF_TRUSTED_ORIGINS.append("https://apps.academie.staging.missionformations.com")


MFE_CONFIG["PARAGON_THEME_URLS"] = {"variants": {"light": {"urls": {"default": "https://raw.githubusercontent.com/edly-io/brand-openedx/refs/heads/ulmo/indigo/dist/light.min.css", "brandOverride": "https://raw.githubusercontent.com/edly-io/brand-openedx/refs/heads/ulmo/indigo/dist/light.min.css"}}, "dark": {"urls": {"default": "https://raw.githubusercontent.com/edly-io/brand-openedx/refs/heads/ulmo/indigo/dist/dark.min.css", "brandOverride": "https://raw.githubusercontent.com/edly-io/brand-openedx/refs/heads/ulmo/indigo/dist/dark.min.css"}}}}


MFE_CONFIG['INDIGO_ENABLE_DARK_TOGGLE'] = True
MFE_CONFIG['INDIGO_FOOTER_NAV_LINKS'] = [{'title': 'Qui sommes-nous', 'url': 'https://missionformations.com/a-propos/qui-sommes-nous/'}, {'title': 'Catalogue', 'url': '/catalogue/'}, {'title': "Centre d'aide", 'url': '/aide/'}, {'title': 'Contact', 'url': '/contact/'}, {'title': 'CGU / CGV', 'url': 'https://missionformations.com/mission-formation-cgu-cgv/'}, {'title': 'Mentions legales', 'url': 'https://missionformations.com/mentions-legales/'}]

PIPELINE['JS_COMPRESSOR'] = None
