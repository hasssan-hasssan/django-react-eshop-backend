from datetime import timedelta  # Used to configure token expiration times for JWT
import os  # Allows access to environment variables and file paths
# Handles loading environment variables from a .env file
from dotenv import load_dotenv
from pathlib import Path  # Provides a convenient way to handle file system paths

# Load environment variables from a .env file
load_dotenv()

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent


#  -------------------------
# | Basic Security Settings |
#  -------------------------

# SECRET_KEY should always remain confidential and never exposed in production
SECRET_KEY = os.getenv('SECRET_KEY')

# DEBUG mode should be False in production to avoid exposing sensitive details
DEBUG = os.getenv('DEBUG') == 'True'

# PRODUCTTION mode
IS_PRODUCTION = os.getenv('IS_PRODUCTION') == 'True'


# Define the hosts allowed to access the application (empty during development)
ALLOWED_HOSTS = [] if not IS_PRODUCTION else os.getenv('ALLOWED_HOSTS').split(',')

#  -----------------------
# | Installed Application |
#  -----------------------

INSTALLED_APPS = [
    # Default Django applications for core functionality
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party applications
    'rest_framework',  # Django REST framework for building APIs
    'rest_framework_simplejwt',  # JWT authentication for DRF
    'rest_framework_simplejwt.token_blacklist',  # Allows token blacklisting
    'corsheaders',  # Handles Cross-Origin Resource Sharing (CORS)

    # Custom applications specific to this project
    'base.apps.BaseConfig',
]


#  ------------
# | Middleware |
#  ------------

MIDDLEWARE = [
    # Enables CORS for APIs
    'corsheaders.middleware.CorsMiddleware',

    # Enhances security features
    'django.middleware.security.SecurityMiddleware',

    # Manages user sessions
    'django.contrib.sessions.middleware.SessionMiddleware',

    # Provides common functionality for requests
    'django.middleware.common.CommonMiddleware',

    # Protects against Cross-Site Request Forgery attacks
    'django.middleware.csrf.CsrfViewMiddleware',

    # Manages user authentication
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Handles user messaging
    'django.contrib.messages.middleware.MessageMiddleware',

    # Protects against clickjacking attacks
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

#  ----------------------------
# | URL and WSGI Configuration |
#  ----------------------------

ROOT_URLCONF = 'backend.urls'  # Specifies the main URL configuration module

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # Template backend engine
        'DIRS': [],  # Optionally add custom template directories here
        'APP_DIRS': True,  # Enables template discovery in installed apps
        'OPTIONS': {
            'context_processors': [

                # Provides debug context
                'django.template.context_processors.debug',

                # Adds the request object to templates
                'django.template.context_processors.request',

                # Adds user authentication context
                'django.contrib.auth.context_processors.auth',

                # Adds messaging context
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'  # WSGI entry point for deployment


#  -------------------
# | Database Settings |
#  -------------------

DATABASES = {
    'default': {
        # Database backend (default: SQLite)
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database/db.sqlite3',  # Path to the SQLite database file
    }
}


#  ---------------------
# | Password Validation |
#  ---------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


#  ----------------------
# | Internationalization |
#  ----------------------

LANGUAGE_CODE = 'en-us'  # Language code for the application
TIME_ZONE = 'Asia/Tehran'  # Default time zone
USE_I18N = True  # Enables translation of text
USE_TZ = True  # Enables timezone-aware datetimes


#  ------------------------
# | Static and Media Files |
#  ------------------------
if IS_PRODUCTION:
    STATIC_URL = '/public/static/'  # URL refix for serving static files
    STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')
    STATICFILES_DIRS = [
        # BASE_DIR / 'static/images',  # Additional directory for static files
    ]
    MEDIA_URL = '/public/media/'  # URL prefix for serving media files
    # Filesystem path for storing media files
    MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    
    
#  --------------------------------
# | Default Primary Key Field Type |
#  --------------------------------

# Default type for auto-generated primary keys
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#  --------------------
# | CORS Configuration |
#  --------------------

if IS_PRODUCTION:
    # Restricts CORS to specific origins in production for better security
    # Only requests from trusted domains will be allowed
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [
        'https://django-react-eshop.ir',  # Primary domain for production
        'http://django-react-eshop.ir',  # Alternate domain for production
    ]
    CSRF_TRUSTED_ORIGINS = [
        "https://api.django-react-eshop.ir",
        "http://api.django-react-eshop.ir",
    ]
else:
    # Allows all origins during development for ease of testing APIs
    CORS_ALLOW_ALL_ORIGINS = True


#  --------------------------------
# | Security Cookies Configuration |
#  --------------------------------

if IS_PRODUCTION:
    # Ensures the CSRF cookie is sent only over secure (HTTPS) connections
    CSRF_COOKIE_SECURE = True
    # Ensures the session cookie is sent only over secure (HTTPS) connections
    SESSION_COOKIE_SECURE = True


#  --------------------------------
# | Django REST Framework Settings |
#  --------------------------------

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # Enable JWT authentication
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}


#  -------------------------
# | SimpleJWT Configuration |
#  -------------------------

SIMPLE_JWT = {
    # Access tokens expire after 5 minutes
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    # Refresh tokens expire after 1 day
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,  # Rotate refresh tokens after every use
    # Blacklist refresh tokens after they are rotated
    "BLACKLIST_AFTER_ROTATION": True,

    "ALGORITHM": "HS256",  # Algorithm used to encode JWTs
    # Custom serializer for obtaining tokens
    "TOKEN_OBTAIN_SERIALIZER": "base.serializers.MyTokenObtainPairSerializer",
}


#  -------------------------------
# | Application-Specific Settings |
#  -------------------------------

# Backend domain loaded from environment variables
BACKEND_DOMAIN = os.getenv('BACKEND_DOMAIN')
# Frontend domain loaded from environment variables
FRONTEND_DOMAIN = os.getenv('FRONTEND_DOMAIN')


#  ---------------------
# | Email Configuration |
#  ---------------------

if IS_PRODUCTION:
    # Use SMTP for sending emails
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    # Use Console to simulate sending emails
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    
EMAIL_HOST = 'smtp.gmail.com'  # SMTP host
EMAIL_PORT = 587  # SMTP port
EMAIL_USE_TLS = True  # Enable TLS for email security
# Email username from environment variables
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# Email password from environment variables
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')


#  -------------------
# | IPG Configuration |
#  -------------------

# Zibal merchant key loaded from environment variables
ZIBAL_MERCHANT = os.getenv('ZIBAL_MERCHANT')
