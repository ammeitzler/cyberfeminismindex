from django.test import TestCase

from cogwheels import BaseAppSettingsHelper, DeprecatedAppSetting
from cogwheels.exceptions import (
    IncorrectDeprecationsValueType, InvalidDeprecationDefinition,
    DuplicateDeprecationError
)


class TestSettingsHelper(BaseAppSettingsHelper):
    defaults_path = 'cogwheels.tests.conf.defaults'
    prefix = 'TEST_'
    deprecations = ()


class TestHelperInitErrors(TestCase):

    def setUp(self):
        # Reset TestSettingsHelper class attributes before each test
        TestSettingsHelper.deprecations = ()

    def test_raises_incorrectdeprecationsvaluetype_if_deprecations_value_is_wrong_type(self):
        TestSettingsHelper.deprecations = {}
        with self.assertRaises(IncorrectDeprecationsValueType):
            TestSettingsHelper()

    def test_raises_correct_error_type_if_deprecated_value_not_found_in_defaults(self):
        TestSettingsHelper.deprecations = (
            DeprecatedAppSetting('NON_EXISTENT_SETTING'),
        )
        with self.assertRaises(InvalidDeprecationDefinition):
            TestSettingsHelper()

    def test_raises_correct_error_type_if_replacement_value_not_found_in_defaults(self):
        TestSettingsHelper.deprecations = (
            DeprecatedAppSetting(
                'DEPRECATED_SETTING', renamed_to="NON_EXISTENT_SETTING"
            ),
        )
        with self.assertRaises(InvalidDeprecationDefinition):
            TestSettingsHelper()

    def test_raises_correct_error_type_if_setting_name_repeated_in_deprecation_definitions(self):
        TestSettingsHelper.deprecations = (
            DeprecatedAppSetting('DEPRECATED_SETTING'),
            DeprecatedAppSetting('DEPRECATED_SETTING'),
        )
        with self.assertRaises(DuplicateDeprecationError):
            TestSettingsHelper()
