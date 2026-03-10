# -*- coding: utf-8 -*-
import os
from cms.envs.production import *

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
MEILISEARCH_API_KEY = "cda467ae1bcfa30dadd2400dd6ea7003b1cbdc0c50628242e0002f803608fb8b"
MEILISEARCH_MASTER_KEY = "6ixf3mqlduT6kM6WcqV02lPo"
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
JWT_AUTH["JWT_SECRET_KEY"] = "Nk7nEpAY2DIIIYG2jx2FsyNy"
JWT_AUTH["JWT_PRIVATE_SIGNING_JWK"] = json.dumps(
    {
        "kid": "openedx",
        "kty": "RSA",
        "e": "AQAB",
        "d": "JEejlTv7sWB21nWT3QcZc0r41jFnuWj__R4ld3keBb2ND8TYkGASZgeIpzFZechFWSqDZr1IWnf0w5RJng7Amnx-1SXflCs9mVkYV3444ATC0pTbeRfFN1hj6u2QJUAMc1G3C8Ng-RdkLDDIegv5dnOEbhth2njrVfeBubpfBS4ZiXpxAqBMgM8dCOozBDzKVd3A5RPs2hAhurH4K7_q-WBQljP3ob7-B5XvUHKw22K15zYwyV1JjeLDsCIUDCaXQCCMQZ3dNpzDRV3kZt7RpbXldqShBPrcKmIUpxjdnn_h7ohtxXiVAVeIi3razh26Z8crzw9p_Fz1r50oufMFAQ",
        "n": "4rQ7STdIxYUuDsDJ-TzjKIdsZ1pcCo_y3vQmzP_wWbdte0MuaBhIAjH1CKQLNPYFHLOQueobhvCODFPl5BXWcAO-CeDfPo4zReAET3CuI3tJA-XJRi5u5GiMrQvKkIFPjrK7AgMLb1Awg7vE5usxEnodVIw0Fb4j5xMhB-kr7Mzus4mau6OYkZumRBPHZZKu8m9hgZgJD0u3o-8UdWK9Z0LpxmFehUU0sHConlx5iE4VLSQgP4RrQ9j9HBjc_lzI_NKKUq-XbhV9i4MLnFU29e05eOBLQzTYWJeIl9urBQll7XDfTREqSR7za_wp0CvmabgQSRYKZOvguj7g3do7kw",
        "p": "72VIA8Q0nYACCVn3g8CkAOg__jL2OAlcnTFHaJm7eJZtK3TopBjCFqTro8dtE9ej8eeHxaGZb0CkP5uZIyYTJkTrfrDi-fnInWVsk-wdwEoE7-fPqQYbEvrylEu4HHxu1tMPtCD0u7TwdKYuNig704-Lb2xiTgd2KMgkkUE0BoM",
        "q": "8m2ZAqHfelu29Mkg2tJvZeuGgkk9_GwiXfFLoPqBBuIiPd3Cl-qw0PKfmkLe9m7FcblOcON7N-IZjybslcNUSuC4Es3g86ebuBD4WkgPB6Wrew38uW_GwL8glY_1W5Vbedtx21uaIDpxCVdkviDMIY70434cxBVuP4waG38SabE",
        "dq": "1sb-fnSHF1JV_vyJ3RP-mZ9WperZvd7Xe78hL9d_pGeHyqPDmO_WAuhROkvwWQe-aYiw1BbVvabU2hy0EeLhtQzuR8qad4OQ1DxEq0eX-UBvci_sLSW4Ql-SMK8_wwnJ52Xhs2OuYsskBhClMkTAVSLgFwRN2_LYn_gx0RZ9a6E",
        "dp": "rpRsxRpjyGwekBVE9JcawvKcIFOnzUu-d4AFdFmQJquEp4lVUr4fZIYWtdRsTmkWzQWstMpZa5F3dk-RiNluY50lI7n5fJTU4Tuix-kL9TvFh_LENJ4YRmotV0o01MlFx3IZ5KGX9_9Gz7qUvrfukSUAaVxgAEleuPTj_e3P8-M",
        "qi": "JKGPuVCsDspe1HhUcdRzro0oZaO_nyn08sBXHXjl_ENPut0JbXq_duyt4JVrPePd1ZGGuJAkAvxe30GxvaWEGoc5u89UK5OWkGOBeoOZg3a7yKD_ZfDx_Yeq9dRtLyf1F3mRR_VBz8squc2H3L0CJ_FK2VGgMemUa8-VFyDm5gA",
    }
)
JWT_AUTH["JWT_PUBLIC_SIGNING_JWK_SET"] = json.dumps(
    {
        "keys": [
            {
                "kid": "openedx",
                "kty": "RSA",
                "e": "AQAB",
                "n": "4rQ7STdIxYUuDsDJ-TzjKIdsZ1pcCo_y3vQmzP_wWbdte0MuaBhIAjH1CKQLNPYFHLOQueobhvCODFPl5BXWcAO-CeDfPo4zReAET3CuI3tJA-XJRi5u5GiMrQvKkIFPjrK7AgMLb1Awg7vE5usxEnodVIw0Fb4j5xMhB-kr7Mzus4mau6OYkZumRBPHZZKu8m9hgZgJD0u3o-8UdWK9Z0LpxmFehUU0sHConlx5iE4VLSQgP4RrQ9j9HBjc_lzI_NKKUq-XbhV9i4MLnFU29e05eOBLQzTYWJeIl9urBQll7XDfTREqSR7za_wp0CvmabgQSRYKZOvguj7g3do7kw",
            }
        ]
    }
)
JWT_AUTH["JWT_ISSUERS"] = [
    {
        "ISSUER": "https://academie.staging.missionformations.com/oauth2",
        "AUDIENCE": "openedx",
        "SECRET_KEY": "Nk7nEpAY2DIIIYG2jx2FsyNy"
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

######## Common CMS settings
STUDIO_NAME = "Mission Formations - Staging - Studio"

CACHES["staticfiles"] = {
    "KEY_PREFIX": "staticfiles_cms",
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    "LOCATION": "staticfiles_cms",
}

# Authentication
SOCIAL_AUTH_EDX_OAUTH2_SECRET = "PAt2eLk4RR9q1GARhUAMdKPe"
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = "http://lms:8000"
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False  # scheme is correctly included in redirect_uri
SESSION_COOKIE_NAME = "studio_session_id"

MAX_ASSET_UPLOAD_FILE_SIZE_IN_MB = 100

FRONTEND_LOGIN_URL = LMS_ROOT_URL + '/login'
FRONTEND_REGISTER_URL = LMS_ROOT_URL + '/register'

# Enable "reindex" button
FEATURES["ENABLE_COURSEWARE_INDEX"] = True

# Create folders if necessary
for folder in [LOG_DIR, MEDIA_ROOT, STATIC_ROOT, ORA2_FILEUPLOAD_ROOT]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

# mission_theme_lock: keep CMS aligned on Mission default theme
DEFAULT_SITE_THEME = "mission-theme"
if "/openedx/themes" not in COMPREHENSIVE_THEME_DIRS:
    COMPREHENSIVE_THEME_DIRS.append("/openedx/themes")

######## End of common CMS settings

ALLOWED_HOSTS = [
    ENV_TOKENS.get("CMS_BASE"),
    "cms",
]
CORS_ORIGIN_WHITELIST.append("https://studio.staging.missionformations.com")

# Authentication
SOCIAL_AUTH_EDX_OAUTH2_KEY = "cms-sso"
SOCIAL_AUTH_EDX_OAUTH2_PUBLIC_URL_ROOT = "https://academie.staging.missionformations.com"

# MFE-specific settings

COURSE_AUTHORING_MICROFRONTEND_URL = "https://apps.academie.staging.missionformations.com/authoring"


LOGIN_REDIRECT_WHITELIST.append("apps.academie.staging.missionformations.com")
CORS_ORIGIN_WHITELIST.append("https://apps.academie.staging.missionformations.com")
CSRF_TRUSTED_ORIGINS.append("https://apps.academie.staging.missionformations.com")
# mission_theme_lock: keep CMS aligned on Mission default theme
DEFAULT_SITE_THEME = "mission-theme"
if "/openedx/themes" not in COMPREHENSIVE_THEME_DIRS:
    COMPREHENSIVE_THEME_DIRS.append("/openedx/themes")PIPELINE['JS_COMPRESSOR'] = None

PIPELINE['JS_COMPRESSOR'] = None
