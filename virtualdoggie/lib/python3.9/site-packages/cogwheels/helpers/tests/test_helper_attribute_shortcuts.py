from unittest.mock import patch

from cogwheels import UnknownSettingNameError
from cogwheels.helpers import BaseAppSettingsHelper
from cogwheels.tests.base import AppSettingTestCase


class TestDirectAttributeShortcut(AppSettingTestCase):

    @patch.object(BaseAppSettingsHelper, 'get')
    def test_raises_unknownsettingnameerror_if_no_default_defined(self, mocked_method):
        expected_message = "'UNKNOWN_SETTING' is not a valid setting name for this helper"
        with self.assertRaisesRegex(UnknownSettingNameError, expected_message):
            self.appsettingshelper.UNKNOWN_SETTING
        mocked_method.assert_not_called()

    @patch.object(BaseAppSettingsHelper, 'get')
    def test_raises_simple_attributeerror_if_non_uppercase_attribute_not_found(self, mocked_method):
        for attribute_name in (
            'lower_case_attr',
            'MIXED_case_attr'
            'CamelCaseAttr'
        ):
            try:
                getattr(self.appsettingshelper, attribute_name)
            except AttributeError as e:
                self.assertNotIsInstance(e, UnknownSettingNameError)
        mocked_method.assert_not_called()


class TestModelsShortcut(AppSettingTestCase):
    """
    Each settings helper instance has a 'models' attribute, which allows
    developers to retrieve Django model classes referenced by setting values
    as attributes, rather than passing the setting name as a string to the
    'get_model()' method.

    The 'get_model()' method is already well tested, so all we want to show
    is that attribute requests are always passed on to that method (unless we
    know there is no such setting).
    """
    @patch.object(BaseAppSettingsHelper, 'get_model')
    def test_raises_unknownsettingnameerror_if_no_default_defined(self, mocked_method):
        expected_message = "'UNKNOWN_SETTING' is not a valid setting name for this helper"
        with self.assertRaisesRegex(UnknownSettingNameError, expected_message):
            self.appsettingshelper.models.UNKNOWN_SETTING
        mocked_method.assert_not_called()

    @patch.object(BaseAppSettingsHelper, 'get_model')
    def test_raises_simple_attributeerror_if_non_uppercase_attribute_not_found(self, mocked_method):
        for attribute_name in (
            'lower_case_attr',
            'MIXED_case_attr'
            'CamelCaseAttr'
        ):
            try:
                getattr(self.appsettingshelper.models, attribute_name)
            except AttributeError as e:
                self.assertNotIsInstance(e, UnknownSettingNameError)
        mocked_method.assert_not_called()

    @patch.object(BaseAppSettingsHelper, 'get_model')
    def test_with_valid_object_setting(self, mocked_method):
        self.appsettingshelper.models.VALID_MODEL
        mocked_method.assert_called_with('VALID_MODEL', warning_stacklevel=5)

    @patch.object(BaseAppSettingsHelper, 'get_model')
    def test_with_invalid_object_setting(self, mocked_method):
        self.appsettingshelper.models.MODULE_UNAVAILABLE_OBJECT
        mocked_method.assert_called_with('MODULE_UNAVAILABLE_OBJECT', warning_stacklevel=5)

    @patch.object(BaseAppSettingsHelper, 'get_model')
    def test_with_completely_different_types_of_setting(self, mocked_method):
        self.appsettingshelper.models.INTEGER_SETTING
        mocked_method.assert_called_with('INTEGER_SETTING', warning_stacklevel=5)
        self.appsettingshelper.models.TUPLES_SETTING
        mocked_method.assert_called_with('TUPLES_SETTING', warning_stacklevel=5)


class TestModulesShortcut(AppSettingTestCase):
    """
    Each settings helper instance has a 'modules' attribute, which allows
    developers to easily retrieve Python modules referenced by setting
    values as attributes, instead of having to pass the setting name as a
    string to the 'get_model()' method.

    The 'get_modules()' method is already well tested, so all we want to show
    is that attribute requests are always passed on to that method (unless we
    know there is no such setting).
    """
    @patch.object(BaseAppSettingsHelper, 'get_module')
    def test_raises_unknownsettingnameerror_if_no_default_defined(self, mocked_method):
        expected_message = "'UNKNOWN_SETTING' is not a valid setting name for this helper"
        with self.assertRaisesRegex(UnknownSettingNameError, expected_message):
            self.appsettingshelper.modules.UNKNOWN_SETTING
        mocked_method.assert_not_called()

    @patch.object(BaseAppSettingsHelper, 'get_module')
    def test_raises_simple_attributeerror_if_non_uppercase_attribute_not_found(self, mocked_method):
        for attribute_name in (
            'lower_case_attr',
            'MIXED_case_attr'
            'CamelCaseAttr'
        ):
            try:
                getattr(self.appsettingshelper.modules, attribute_name)
            except AttributeError as e:
                self.assertNotIsInstance(e, UnknownSettingNameError)
        mocked_method.assert_not_called()

    @patch.object(BaseAppSettingsHelper, 'get_module')
    def test_with_valid_object_setting(self, mocked_method):
        self.appsettingshelper.modules.VALID_MODULE
        mocked_method.assert_called_with('VALID_MODULE', warning_stacklevel=5)

    @patch.object(BaseAppSettingsHelper, 'get_module')
    def test_with_invalid_object_setting(self, mocked_method):
        self.appsettingshelper.modules.MODULE_UNAVAILABLE_OBJECT
        mocked_method.assert_called_with('MODULE_UNAVAILABLE_OBJECT', warning_stacklevel=5)

    @patch.object(BaseAppSettingsHelper, 'get_module')
    def test_with_completely_different_types_of_setting(self, mocked_method):
        self.appsettingshelper.modules.INTEGER_SETTING
        mocked_method.assert_called_with('INTEGER_SETTING', warning_stacklevel=5)
        self.appsettingshelper.modules.TUPLES_SETTING
        mocked_method.assert_called_with('TUPLES_SETTING', warning_stacklevel=5)


class TestObjectsShortcut(AppSettingTestCase):
    """
    Each settings helper instance has a 'objects' attribute, which allows
    developers to access 'python objects' as attributes, instead of having to
    pass the setting name as a string to the 'get_object()' method.

    The 'get_object()' method is already well tested, so all we want to show
    is that request are always passed on to that method, unless there is no
    default value defined
    """
    @patch.object(BaseAppSettingsHelper, 'get_object')
    def test_raises_unknownsettingnameerror_if_setting_not_in_defaults(self, mocked_method):
        expected_message = "'UNKNOWN_SETTING' is not a valid setting name for this helper"
        with self.assertRaisesRegex(UnknownSettingNameError, expected_message):
            self.appsettingshelper.objects.UNKNOWN_SETTING
        mocked_method.assert_not_called()

    @patch.object(BaseAppSettingsHelper, 'get_object')
    def test_raises_simple_attributeerror_if_non_uppercase_attribute_not_found(self, mocked_method):
        for attribute_name in (
            'lower_case_attr',
            'MIXED_case_attr'
            'CamelCaseAttr'
        ):
            try:
                getattr(self.appsettingshelper.objects, attribute_name)
            except AttributeError as e:
                self.assertNotIsInstance(e, UnknownSettingNameError)
        mocked_method.assert_not_called()

    @patch.object(BaseAppSettingsHelper, 'get_object')
    def test_with_valid_object_setting(self, mocked_method):
        self.appsettingshelper.objects.VALID_OBJECT
        mocked_method.assert_called_with('VALID_OBJECT', warning_stacklevel=5)

    @patch.object(BaseAppSettingsHelper, 'get_object')
    def test_with_invalid_object_setting(self, mocked_method):
        self.appsettingshelper.objects.MODULE_UNAVAILABLE_OBJECT
        mocked_method.assert_called_with('MODULE_UNAVAILABLE_OBJECT', warning_stacklevel=5)

    @patch.object(BaseAppSettingsHelper, 'get_object')
    def test_with_completely_different_types_of_setting(self, mocked_method):
        self.appsettingshelper.objects.INTEGER_SETTING
        mocked_method.assert_called_with('INTEGER_SETTING', warning_stacklevel=5)
        self.appsettingshelper.objects.TUPLES_SETTING
        mocked_method.assert_called_with('TUPLES_SETTING', warning_stacklevel=5)
