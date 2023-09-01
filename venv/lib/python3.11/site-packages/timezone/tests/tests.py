"""
Tests for ``timezone`` app.
"""

# WebTest API docs: http://webtest.readthedocs.org/en/latest/api.html

# from django.utils import timezone as django_timezone
from django_webtest import WebTest

from timezone import timezone


class Timezone(WebTest):
    def test_date(self):
        self.assertTrue(timezone.date())

    def test_datetime(self):
        self.assertTrue(timezone.datetime(1999, 12, 31))

    def test_get(self):
        self.assertTrue(timezone.get())

    def test_jstime(self):
        self.assertTrue(timezone.jstime())

    def test_localize(self):
        self.assertTrue(timezone.localize())
        with self.settings(USE_TZ=True):
            self.assertTrue(timezone.localize())

    def test_midnight(self):
        self.assertTrue(timezone.midnight())
        with self.settings(USE_TZ=True):
            self.assertTrue(timezone.midnight())

    def test_now(self):
        self.assertTrue(timezone.now())

    def test_parse(self):
        self.assertEqual(
            timezone.parse('1999-12-31 00:00', 'Australia/Sydney'),
            timezone.datetime(1999, 12, 31, 0, 0, tzinfo='Australia/Sydney'),
        )
        with self.assertRaises(ValueError):
            timezone.parse('foo')

    def test_strftime(self):
        # Localize to UTC before formatting.
        when = timezone.datetime(1999, 12, 31, 0, 1, tzinfo='Australia/Sydney')
        self.assertEqual(
            timezone.strftime(when, '%B %d, %Y at %H:%I', tz='UTC'),
            'December 30, 1999 at 13:01',
        )

    def test_time(self):
        self.assertTrue(timezone.time())
