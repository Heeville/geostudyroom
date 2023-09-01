"""
Test settings for ``timezone`` app.
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

INSTALLED_APPS = (
    'django_nose',
    'timezone.tests'
)

SECRET_KEY = 'secret-key'
STATIC_URL = '/static/'
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TIME_ZONE = 'Australia/Sydney'
USE_TZ = True
