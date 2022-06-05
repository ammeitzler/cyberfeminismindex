from django.test import TestCase

from cogwheels import BaseAppSettingsHelper


class TestSettingsHelper(BaseAppSettingsHelper):
    pass


class TestSettingsHelperInit(TestCase):

    def setUp(self):
        # Reset TestSettingsHelper class attributes before each test
        TestSettingsHelper.defaults_path = 'cogwheels.tests.conf.defaults'
        TestSettingsHelper.prefix = None
        TestSettingsHelper.deprecations = ()

    def test_set_prefix_converts_specified_value_to_uppercase(self):
        lowercase_prefix = 'beep'
        uppercase_prefix = 'BEEP'

        TestSettingsHelper.prefix = lowercase_prefix
        obj = TestSettingsHelper()
        self.assertEqual(obj._prefix, uppercase_prefix)

    def test_set_prefix_strips_trailing_underscores_from_specified_value(self):
        TestSettingsHelper.prefix = 'TEST___'
        obj = TestSettingsHelper()
        self.assertEqual(obj._prefix, 'TEST')

    def test_importerror_raised_if_defaults_module_does_not_exist(self):
        TestSettingsHelper.defaults_path = 'invalid.module.path'
        with self.assertRaises(ImportError):
            TestSettingsHelper()
