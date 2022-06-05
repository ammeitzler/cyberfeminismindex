from collections import defaultdict
from importlib import import_module
from django.conf import settings as django_settings
from django.core.signals import setting_changed
from cogwheels import (
    OverrideValueError, OverrideValueTypeInvalid,
    OverrideValueFormatInvalid, OverrideValueNotImportable,
    DefaultValueError, DefaultValueTypeInvalid,
    DefaultValueFormatInvalid, DefaultValueNotImportable,
    UnknownSettingNameError
)
from cogwheels.exceptions.deprecations import (
    IncorrectDeprecationsValueType, InvalidDeprecationDefinition,
    DuplicateDeprecationError,
)
from .utils import AttrReferToMethodHelper


class BaseAppSettingsHelper:
    """
    A base class that provides the core functionality that allows developers to
    integrate user overridable settings into their app. This class is not
    intended to be used directly; rather app developers should subclass it to
    define individual 'settings helper' classes for each app.

    Each settings helper instance is associated with a single 'defaults' module,
    where developers define the settings they wish to use/support for each app,
    along with the default values for each setting.

    When a setting value is requested from a settings helper instance, it
    checks the environmment's Django settings module for an override
    value with the relevant name (a prefixed version of the variable defined in
    the ``defaults`` module), and returns that if found. If no override was
    found, the default value defined for the setting is returned instead.

    Some app settings may refer to Django models, Python modules, classes or
    methods, in which case a settings helper instance's ``get_model()``,
    ``get_module()`` and ``get_object()`` methods can be used to import and
    return the objects themselves (provided the raw setting values are valid
    'import path' strings).

    App settings can be deprecated by defining a list of
    ``DeprecatedAppSetting`` instances on the relevant (app specific) helper
    class, causing the settings helper instance to automatically raise
    deprecation warnings where appropriate.
    """

    prefix = None
    defaults_path = None
    deprecations = ()

    def __init__(self):
        self.__module_path_split = self.__class__.__module__.split('.')
        self._set_prefix()

        # Load values from defaults module
        self._load_defaults()

        # Load deprecation data
        self._prepare_deprecation_data()

        # This will create the dictionaries if they don't already exist
        self.reset_caches()

        # Define 'attribute reference' shortcuts
        self.models = AttrReferToMethodHelper(self, 'get_model')
        self.modules = AttrReferToMethodHelper(self, 'get_module')
        self.objects = AttrReferToMethodHelper(self, 'get_object')

        setting_changed.connect(self.reset_caches, dispatch_uid=id(self))

    def __getattr__(self, name):
        """
        Overrides default Python object behavior to allow direct attribute
        requests to be routed to ``get()``, making these lines equivalent::

            appsettingshelper.SETTING_NAME
            appsettingshelper.get('SETTING_NAME')

        Raises an ``AttributeError`` if the requested attribute is not a valid
        setting name.
        """
        if not name.isupper():
            raise AttributeError("{} object has no attribute '{}'".format(
                self.__class__.__name__, name))
        if not self.in_defaults(name):
            self._raise_invalid_setting_name_error(name)
        return self.get(name, warning_stacklevel=4)

    def _set_prefix(self):
        """
        Called by ``__init()__`` to set the object's ``_prefix`` attribute,
        which determines the prefix app users must use when overriding
        settings associated with this helper. For example:

        If the ``_prefix`` attribute were to be set to "YOURAPP", and there
        exists an app setting called ``SETTING_NAME``, app users would override
        that setting by adding a variable with the name ``YOURAPP_SETTING_NAME``
        to their Django settings.

        Developers can choose their own prefix by setting the ``prefix``
        attribute on their helper class. If no value is specified, a deterministic
        default value is generated, based on the where the helper class is defined.
        For example:

        A helper class defined in ``yourapp/conf/settings.py`` or
        ``yourapp/settings.py`` would be assigned the prefix: ``"YOURAPP"``.

        A helper class is defined in ``yourapp/subapp/conf/settings.py`` or
        ``yourapp/subapp/settings.py`` would be assigned the prefix: ``"YOURAPP_SUBAPP"``.
        """
        if self.prefix is not None:
            value = self.prefix.rstrip('_')
        else:
            module_path_parts = self.__module_path_split[:-1]
            if module_path_parts[-1] == 'conf':
                module_path_parts.pop()
            value = '_'.join(module_path_parts)
        self._prefix = value.upper()

    @staticmethod
    def _do_import(module_path):
        """A simple wrapper for importlib.import_module()."""
        return import_module(module_path)

    @staticmethod
    def _make_cache_key(setting_name, accept_deprecated):
        key = setting_name
        if accept_deprecated:
            key += '_accepting_' + str(accept_deprecated)
        return key

    def _load_defaults(self):
        """
        Called by ``__init__()`` to create a dictionary of the relevant
        values from the associated defaults module, and save it to the
        object's ``_defaults`` attribute to improve lookup performance.
        Only variables with upper-case names are included.

        :raises: ImportError

        It is assumed that the defaults module is defined in the same directory
        as ``settings.py`` where the settings helper class is defined. But,
        in cases where this differs, developers can specify an alternative
        import path using the ``defaults_path`` class attribute for their
        helper class.
        """
        self._defaults_module_path = self.defaults_path or \
            '.'.join(self.__module_path_split[:-1]) + ".defaults"

        module = self._do_import(self._defaults_module_path)
        self._defaults = {
            k: v for k, v in module.__dict__.items()
            if k.isupper()
        }

    def _prepare_deprecation_data(self):
        """
        Cycles through the list of AppSettingDeprecation instances set on
        ``self.deprecations`` and prepulates two new dictionary attributes:

        ``self._deprecated_settings``:
            Uses the deprecated setting names themselves as the keys. Used to
            check whether a request is for a deprecated setting.

        ``self._renamed_settings``:
            Uses the 'replacement setting' names as keys (where supplied).
            Used to allow the helper to temporarily support override settings
            defined using the old name, when the values for the new setting are
            requested.
        """
        if not isinstance(self.deprecations, (list, tuple)):
            raise IncorrectDeprecationsValueType(
                "'deprecations' must be a list or tuple, not a {}."
                .format(type(self.deprecations).__name__)
            )

        self._deprecated_settings = {}
        self._replacement_settings = defaultdict(list)

        for item in self.deprecations:
            item.prefix = self.get_prefix()

            if not self.in_defaults(item.setting_name):
                raise InvalidDeprecationDefinition(
                    "There is an issue with one of your setting deprecation "
                    "definitions. '{setting_name}' could not be found in "
                    "{defaults_module_path}. Please ensure a default value "
                    "remains there until the end of the setting's deprecation "
                    "period.".format(
                        setting_name=item.setting_name,
                        defaults_module_path=self._defaults_module_path,
                    )
                )

            if item.setting_name in self._deprecated_settings:
                raise DuplicateDeprecationError(
                    "The setting name for each deprecation definition must be "
                    "unique, but '{setting_name}' has been used more than once "
                    "for {helper_class}.".format(
                        setting_name=item.setting_name,
                        helper_class=self.__class__.__name__,
                    )
                )

            self._deprecated_settings[item.setting_name] = item

            if item.replacement_name:

                if not self.in_defaults(item.replacement_name):
                    raise InvalidDeprecationDefinition(
                        "There is an issue with one of your settings "
                        "deprecation definitions. '{replacement_name}' is not "
                        "a valid replacement for '{setting_name}', as no such "
                        "value can be found in {defaults_module_path}."
                        .format(
                            replacement_name=item.replacement_name,
                            setting_name=item.setting_name,
                            defaults_module_path=self._defaults_module_path,
                        )
                    )

                self._replacement_settings[item.replacement_name].append(item)

    def reset_caches(self, **kwargs):
        """
        Called by ``__init__()`` to initialise the caches for a helper instance.
        It is also called by Django's ``setting_changed`` signal to clear the
        caches when changes to settings are made.

        Although it requires slightly more memory, separate dictionaries are
        used for raw values, models, modules and other objects to help with
        lookup performance for each type.
        """
        self._raw_cache = {}
        self._models_cache = {}
        self._modules_cache = {}
        self._objects_cache = {}

    def in_defaults(self, setting_name):
        return setting_name in self._defaults

    def get_default_value(self, setting_name):
        return self._defaults[setting_name]

    def get_prefix(self):
        return self._prefix + '_'

    def get_prefixed_setting_name(self, setting_name):
        return self.get_prefix() + setting_name

    def get_user_defined_value(self, setting_name):
        attr_name = self.get_prefixed_setting_name(setting_name)
        return getattr(django_settings, attr_name)

    def is_overridden(self, setting_name):
        attr_name = self.get_prefixed_setting_name(setting_name)
        return hasattr(django_settings, attr_name)

    def _raise_invalid_setting_name_error(self, setting_name):
        raise UnknownSettingNameError(
            "'{setting_name}' is not a valid setting name for this helper, as "
            "no such variable can be found in {defaults_module_path}. Valid "
            "setting names are: {valid_names}.".format(
                setting_name=setting_name,
                defaults_module_path=self._defaults_module_path,
                valid_names=', '.join("'%s'" % v for v in self._defaults.keys())
            )
        )

    def _raise_setting_value_error(
        self, setting_name, additional_text,
        user_value_error_class=None, default_value_error_class=None,
        **text_format_kwargs
    ):
        if self.is_overridden(setting_name):
            error_class = user_value_error_class or OverrideValueError
            message = (
                "There is an issue with the value specified for "
                "{setting_name} in your project's Django settings."
            ).format(setting_name=self.get_prefixed_setting_name(setting_name))
        else:
            error_class = default_value_error_class or DefaultValueError
            message = (
                "There is an issue with the default value specified for "
                "{setting_name} in {defaults_module}."
            ).format(
                setting_name=setting_name,
                defaults_module=self._defaults_module_path,
            )

        message += ' ' + additional_text.format(**text_format_kwargs)
        raise error_class(message)

    def _warn_if_deprecated_setting_value_requested(
        self, setting_name, warn_only_if_overridden, suppress_warnings,
        warning_stacklevel,
    ):
        """
        get(), get_object(), get_model() and get_module() must all check
        whether a requested app setting is deprecated. This method allows
        the helper to do that in a DRY/consistent way.
        """
        if(
            not suppress_warnings and
            not warn_only_if_overridden and
            setting_name in self._deprecated_settings
        ):
            depr = self._deprecated_settings[setting_name]
            depr.warn_if_deprecated_setting_value_requested(warning_stacklevel + 1)

    def _get_raw_value(self, setting_name, accept_deprecated='',
                       warn_if_overridden=False, suppress_warnings=False,
                       warning_stacklevel=3):
        """
        Returns the original/raw value for an app setting with the name
        ``setting_name``, exactly as it has been defined in the defaults
        module or a user's Django settings.

        If the requested setting is deprecated, ``warn_if_overridden`` is
        ``True``, and the setting is overridden by a user, a suitable
        deprecation warning is raised to help inform them of the change.

        If the requested setting replaces a single deprecated setting, and no
        user defined setting is defined using the new name, the method will
        look for a user defined setting using the deprecated setting name, and
        return that if found. A deprecation warning will also be raised.

        If the requested setting replaces multiple deprecated settings, the
        ``accept_deprecated`` keyword argument can be used to specify which of
        those deprecated settings to accept as the value if defined by a user.

        If no override value was found in the Django setting, then the
        relevant value from the defaults module is returned.
        """
        if not self.in_defaults(setting_name):
            self._raise_invalid_setting_name_error(setting_name)

        if self.is_overridden(setting_name):
            if(
                warn_if_overridden and not suppress_warnings and
                setting_name in self._deprecated_settings
            ):
                depr = self._deprecated_settings[setting_name]
                depr.warn_if_overridden(warning_stacklevel)
            return self.get_user_defined_value(setting_name)

        if setting_name in self._replacement_settings:
            deprecations = self._replacement_settings[setting_name]
            for item in deprecations:
                if(
                    (len(deprecations) == 1 or item.setting_name == accept_deprecated) and
                    self.is_overridden(item.setting_name)
                ):
                    if not suppress_warnings:
                        item.warn_if_user_using_old_setting_name(warning_stacklevel)
                    return self.get_user_defined_value(item.setting_name)
        return self.get_default_value(setting_name)

    def get(self, setting_name, warn_only_if_overridden=False,
            accept_deprecated='', suppress_warnings=False,
            enforce_type=None, check_if_setting_deprecated=True,
            warning_stacklevel=3):
        """
        Returns a setting value for the setting named by ``setting_name``. The
        returned value is actually a reference to the original setting value,
        so care should be taken to avoid setting the result to a different
        value.

        :param setting_name:
            The name of the app setting for which a value is required.
        :type setting_name: str (e.g. "SETTING_NAME")
        :param warn_only_if_overridden:
            If the setting named by ``setting_name`` is deprecated, a value of
            ``True`` can be provided to silence the immediate deprecation
            warning that is otherwise raised by default. Instead, a
            (differently worded) deprecation warning will be raised, but only
            when the setting is overriden.
        :type warn_only_if_overridden: bool
        :param accept_deprecated:
            If the setting named by ``setting_name`` replaces multiple
            deprecated settings, the ``accept_deprecated`` keyword argument can
            be used to specify which of those deprecated settings to accept as
            an override value.

            Where the requested setting replaces only a single deprecated
            setting, override values for that deprecated setting will be
            accepted automatically, without having to specify anything.
        :type accept_deprecated: str (e.g. "DEPRECATED_SETTING_NAME")
        :param suppress_warnings:
            Use this to prevent the raising of any deprecation warnings that
            might otherwise be raised. It may be more useful to use
            ``warn_only_if_overridden`` instead.
        :type suppress_warnings: bool
        :param enforce_type:
            When a setting value of a specific type is required, this can be
            used to apply some basic validation at the time of retrieval. If
            supplied, and setting value is found not to be an instance of the
            supplied type, a ``SettingValueTypeInvalid`` error will be raised.

            In cases where more than one type of value is accepted, a tuple of
            acceptable types can be provided.
        :type enforce_type: A type (class), or tuple of types
        :param check_if_setting_deprecated:
            Can be used to disable the check that usually happens at the
            beginning of the method to identify whether the setting named by
            ``setting_name`` is deprecated, and conditionally raise a warning.
            This can help to improve efficiency where the same check has
            already been made.
        :type check_if_setting_deprecated: bool
        :param warning_stacklevel:
            When raising deprecation warnings related to the request, this
            value is passed on as ``stacklevel`` to Python's
            ``warnings.warn()`` method, to help give a more accurate indication
            of the code that caused the warning to be raised.
        :type warning_stacklevel: int
        :raises: UnknownSettingNameError, SettingValueTypeInvalid

        Instead of calling this method directly, developers are generally
        encouraged to use the direct attribute shortcut, which is a
        syntactically much cleaner way to request values using the default
        options. For example, the the following lines are equivalent::

            appsettingshelper.SETTING_NAME
            appsettingshelper.get('SETTING_NAME')
        """
        if check_if_setting_deprecated:
            self._warn_if_deprecated_setting_value_requested(
                setting_name, warn_only_if_overridden, suppress_warnings,
                warning_stacklevel)

        cache_key = self._make_cache_key(setting_name, accept_deprecated)
        if cache_key in self._raw_cache:
            return self._raw_cache[cache_key]

        result = self._get_raw_value(
            setting_name,
            accept_deprecated=accept_deprecated,
            warn_if_overridden=warn_only_if_overridden,
            suppress_warnings=suppress_warnings,
            warning_stacklevel=warning_stacklevel + 1,
        )

        if enforce_type and not isinstance(result, enforce_type):
            if isinstance(enforce_type, tuple):
                msg = (
                    "The value is expected to be one of the following types, "
                    "but a value of type '{current_type}' was found: "
                    "{required_types}."
                )
                text_format_kwargs = dict(
                    current_type=type(result).__name__,
                    required_types=enforce_type,
                )
            else:
                msg = (
                    "The value is expected to be a '{required_type}', but a "
                    "value of type '{current_type}' was found."
                )
                text_format_kwargs = dict(
                    current_type=type(result).__name__,
                    required_type=enforce_type.__name__,
                )
            self._raise_setting_value_error(
                setting_name=setting_name,
                user_value_error_class=OverrideValueTypeInvalid,
                default_value_error_class=DefaultValueTypeInvalid,
                additional_text=msg,
                **text_format_kwargs
            )
        self._raw_cache[cache_key] = result
        return result

    def get_model(self, setting_name, warn_only_if_overridden=False,
                  accept_deprecated='', suppress_warnings=False,
                  warning_stacklevel=3):
        """
        Returns a Django model referenced by an app setting where the value is
        expected to be a valid 'model string' in the format:
        "app_label.model_name".

        :param setting_name:
            The name of the app setting for which a value is required.
        :type setting_name: str (e.g. "SETTING_NAME")
        :param warn_only_if_overridden:
            If the setting named by ``setting_name`` is deprecated, a value of
            ``True`` can be provided to silence the immediate deprecation
            warning that is otherwise raised by default. Instead, a
            (differently worded) deprecation warning will be raised, but only
            when the setting is overriden.
        :type warn_only_if_overridden: bool
        :param accept_deprecated:
            If the setting named by ``setting_name`` replaces multiple
            deprecated settings, the ``accept_deprecated`` keyword argument can
            be used to specify which of those deprecated settings to accept as
            an override value.

            Where the requested setting replaces only a single deprecated
            setting, override values for that deprecated setting will be
            accepted automatically, without having to specify anything.
        :type accept_deprecated: str (e.g. "DEPRECATED_SETTING_NAME")
        :param suppress_warnings:
            Use this to prevent the raising of any deprecation warnings that
            might otherwise be raised. It may be more useful to use
            ``warn_only_if_overridden`` instead.
        :type suppress_warnings: bool
        :param warning_stacklevel:
            When raising deprecation warnings related to the request, this
            value is passed on as ``stacklevel`` to Python's
            ``warnings.warn()`` method, to help give a more accurate indication
            of the code that caused the warning to be raised.
        :type warning_stacklevel: int
        :raises:
            UnknownSettingNameError, SettingValueTypeInvalid,
            SettingValueFormatInvalid, SettingValueNotImportable

        Instead of calling this method directly, developers are generally
        encouraged to use the ``models`` attribute shortcut, which is a
        syntactically much cleaner way to request values using the default
        options. For example, the the following lines are equivalent::

            appsettingshelper.models.SETTING_NAME
            appsettingshelper.get_model('SETTING_NAME')

        """
        self._warn_if_deprecated_setting_value_requested(
            setting_name, warn_only_if_overridden, suppress_warnings,
            warning_stacklevel)

        cache_key = self._make_cache_key(setting_name, accept_deprecated)
        if cache_key in self._models_cache:
            return self._models_cache[cache_key]

        raw_value = self.get(
            setting_name,
            enforce_type=str,
            accept_deprecated=accept_deprecated,
            check_if_setting_deprecated=False,
            warn_only_if_overridden=warn_only_if_overridden,
            suppress_warnings=suppress_warnings,
            warning_stacklevel=warning_stacklevel + 1,
        )

        try:
            from django.apps import apps  # delay import until needed
            result = apps.get_model(raw_value)
            self._models_cache[cache_key] = result
            return result
        except ValueError:
            self._raise_setting_value_error(
                setting_name=setting_name,
                user_value_error_class=OverrideValueFormatInvalid,
                default_value_error_class=DefaultValueFormatInvalid,
                additional_text=(
                    "Model strings should match the format 'app_label.Model', "
                    "which '{value}' does not adhere to."
                ),
                value=raw_value,
            )
        except LookupError:
            self._raise_setting_value_error(
                setting_name=setting_name,
                user_value_error_class=OverrideValueNotImportable,
                default_value_error_class=DefaultValueNotImportable,
                additional_text=(
                    "The model '{value}' does not appear to be installed."
                ),
                value=raw_value
            )

    def get_module(self, setting_name, warn_only_if_overridden=False,
                   accept_deprecated='', suppress_warnings=False,
                   warning_stacklevel=3):
        """
        Returns a Python module referenced by an app setting where the value is
        expected to be a valid, absolute Python import path, defined as a
        string (e.g. "myproject.app.custom_module").

        :param setting_name:
            The name of the app setting for which a value is required.
        :type setting_name: str (e.g. "SETTING_NAME")
        :param warn_only_if_overridden:
            If the setting named by ``setting_name`` is deprecated, a value of
            ``True`` can be provided to silence the immediate deprecation
            warning that is otherwise raised by default. Instead, a
            (differently worded) deprecation warning will be raised, but only
            when the setting is overriden.
        :type warn_only_if_overridden: bool
        :param accept_deprecated:
            If the setting named by ``setting_name`` replaces multiple
            deprecated settings, the ``accept_deprecated`` keyword argument can
            be used to specify which of those deprecated settings to accept as
            an override value.

            Where the requested setting replaces only a single deprecated
            setting, override values for that deprecated setting will be
            accepted automatically, without having to specify anything.
        :type accept_deprecated: str (e.g. "DEPRECATED_SETTING_NAME")
        :param suppress_warnings:
            Use this to prevent the raising of any deprecation warnings that
            might otherwise be raised. It may be more useful to use
            ``warn_only_if_overridden`` instead.
        :type suppress_warnings: bool
        :param warning_stacklevel:
            When raising deprecation warnings related to the request, this
            value is passed on as ``stacklevel`` to Python's
            ``warnings.warn()`` method, to help give a more accurate indication
            of the code that caused the warning to be raised.
        :type warning_stacklevel: int
        :raises:
            UnknownSettingNameError, SettingValueTypeInvalid,
            SettingValueNotImportable

        Instead of calling this method directly, developers are generally
        encouraged to use the ``modules`` attribute shortcut, which is a
        syntactically much cleaner way to request values using the default
        options. For example, the the following lines are equivalent::

            appsettingshelper.modules.SETTING_NAME
            appsettingshelper.get_module('SETTING_NAME')

        """
        self._warn_if_deprecated_setting_value_requested(
            setting_name, warn_only_if_overridden, suppress_warnings,
            warning_stacklevel)

        cache_key = self._make_cache_key(setting_name, accept_deprecated)
        if cache_key in self._modules_cache:
            return self._modules_cache[cache_key]

        raw_value = self.get(
            setting_name,
            enforce_type=str,
            accept_deprecated=accept_deprecated,
            check_if_setting_deprecated=False,
            warn_only_if_overridden=warn_only_if_overridden,
            suppress_warnings=suppress_warnings,
            warning_stacklevel=warning_stacklevel + 1,
        )

        try:
            result = self._do_import(raw_value)
            self._modules_cache[cache_key] = result
            return result
        except ImportError:
            self._raise_setting_value_error(
                setting_name=setting_name,
                user_value_error_class=OverrideValueNotImportable,
                default_value_error_class=DefaultValueNotImportable,
                additional_text=(
                    "No module could be found matching the path '{value}'. "
                    "Please use a full (not relative) import path in the "
                    "format: 'project.app.module'."
                ),
                value=raw_value
            )

    def get_object(self, setting_name, warn_only_if_overridden=False,
                   accept_deprecated='', suppress_warnings=False,
                   warning_stacklevel=3):
        """
        Returns a python class, method, or other object referenced by an app
        setting where the value is expected to be a valid, absolute Python
        import path, defined as a string (e.g. "myproject.app.module.MyClass").

        :param setting_name:
            The name of the app setting for which a value is required.
        :type setting_name: str (e.g. "SETTING_NAME")
        :param warn_only_if_overridden:
            If the setting named by ``setting_name`` is deprecated, a value of
            ``True`` can be provided to silence the immediate deprecation
            warning that is otherwise raised by default. Instead, a
            (differently worded) deprecation warning will be raised, but only
            when the setting is overriden.
        :type warn_only_if_overridden: bool
        :param accept_deprecated:
            If the setting named by ``setting_name`` replaces multiple
            deprecated settings, the ``accept_deprecated`` keyword argument can
            be used to specify which of those deprecated settings to accept as
            an override value.

            Where the requested setting replaces only a single deprecated
            setting, override values for that deprecated setting will be
            accepted automatically, without having to specify anything.
        :type accept_deprecated: str (e.g. "DEPRECATED_SETTING_NAME")
        :param suppress_warnings:
            Use this to prevent the raising of any deprecation warnings that
            might otherwise be raised. It may be more useful to use
            ``warn_only_if_overridden`` instead.
        :type suppress_warnings: bool
        :param warning_stacklevel:
            When raising deprecation warnings related to the request, this
            value is passed on as ``stacklevel`` to Python's
            ``warnings.warn()`` method, to help give a more accurate indication
            of the code that caused the warning to be raised.
        :type warning_stacklevel: int
        :raises:
            UnknownSettingNameError, SettingValueTypeInvalid,
            SettingValueFormatInvalid, SettingValueNotImportable

        Instead of calling this method directly, developers are generally
        encouraged to use the ``objects`` attribute shortcut, which is a
        syntactically much cleaner way to request values using the default
        options. For example, the the following lines are equivalent::

            appsettingshelper.objects.SETTING_NAME
            appsettingshelper.get_object('SETTING_NAME')

        """
        self._warn_if_deprecated_setting_value_requested(
            setting_name, warn_only_if_overridden, suppress_warnings,
            warning_stacklevel)

        cache_key = self._make_cache_key(setting_name, accept_deprecated)
        if cache_key in self._objects_cache:
            return self._objects_cache[cache_key]

        raw_value = self.get(
            setting_name,
            enforce_type=str,
            accept_deprecated=accept_deprecated,
            check_if_setting_deprecated=False,
            warn_only_if_overridden=warn_only_if_overridden,
            suppress_warnings=suppress_warnings,
            warning_stacklevel=warning_stacklevel + 1,
        )
        try:
            module_path, object_name = raw_value.rsplit(".", 1)
        except ValueError:
            self._raise_setting_value_error(
                setting_name=setting_name,
                user_value_error_class=OverrideValueFormatInvalid,
                default_value_error_class=DefaultValueFormatInvalid,
                additional_text=(
                    "'{value}' is not a valid object import path. Please use "
                    "a full (not relative) import path with the object name "
                    "at the end, for example: 'project.app.module.object'."
                ),
                value=raw_value
            )
        try:
            result = getattr(self._do_import(module_path), object_name)
            self._objects_cache[cache_key] = result
            return result
        except ImportError:
            self._raise_setting_value_error(
                setting_name=setting_name,
                user_value_error_class=OverrideValueNotImportable,
                default_value_error_class=DefaultValueNotImportable,
                additional_text=(
                    "No module could be found matching the path "
                    "'{module_path}'. Please use a full (not relative) import "
                    "path with the object name at the end, for example: "
                    "'project.app.module.object'."
                ),
                module_path=module_path,
            )
        except AttributeError:
            self._raise_setting_value_error(
                setting_name=setting_name,
                user_value_error_class=OverrideValueNotImportable,
                default_value_error_class=DefaultValueNotImportable,
                additional_text=(
                    "No object could be found in {module_path} matching the "
                    "name '{object_name}'."
                ),
                module_path=module_path,
                object_name=object_name,
            )

    def is_value_from_deprecated_setting(self, setting_name, deprecated_setting_name):
        """
        Helps developers to determine where the settings helper got it's value
        from when dealing with settings that replace deprecated settings.

        Returns ``True`` when the new setting (with the name ``setting_name``)
        is a replacement for a deprecated setting (with the name
        ``deprecated_setting_name``) and the user is using the deprecated
        setting in their Django settings to override behaviour.
        """
        if not self.in_defaults(setting_name):
            self._raise_invalid_setting_name_error(setting_name)
        if not self.in_defaults(deprecated_setting_name):
            self._raise_invalid_setting_name_error(deprecated_setting_name)
        if deprecated_setting_name not in self._deprecated_settings:
            raise ValueError(
                "The '%s' setting is not deprecated. When using "
                "settings.is_value_from_deprecated_setting(), the deprecated "
                "setting name should be supplied as the second argument." %
                deprecated_setting_name
            )
        if(
            not self.is_overridden(setting_name) and
            setting_name in self._replacement_settings
        ):
            deprecations = self._replacement_settings[setting_name]
            for item in deprecations:
                if(
                    item.setting_name == deprecated_setting_name and
                    self.is_overridden(item.setting_name)
                ):
                    return True
        return False
