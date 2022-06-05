class AttrReferToMethodHelper:
    """
    Each settings helper defines several instances of this class as attributes,
    to provide a cleaner way to access Django models, Python modules and other
    objects from setting values. Each instance essentially just forwards
    request to the relevant 'get_x()' method on the helper itself.

    For example::

        # For accessing Django models, these are equivalent:
        appsettingshelper.get_model("MODEL_SETTING_NAME")
        appsettingshelper.models.MODEL_SETTING_NAME

        # For accessing Python modules, these are equivalent:
        appsettingshelper.get_module("MODULE_SETTING_NAME")
        appsettingshelper.modules.MODULE_SETTING_NAME

        # For accessing other Python objects, these are equivalent:
        appsettingshelper.get_object("OBJECT_SETTING_NAME")
        appsettingshelper.objects.OBJECT_SETTING_NAME

    """
    def __init__(self, settings_helper, getter_method_name):
        self.settings_helper = settings_helper
        self.getter_method_name = getter_method_name

    def __getattr__(self, name):
        if not name.isupper():
            raise AttributeError("{} object has no attribute '{}'".format(
                self.__class__.__name__, name))
        if not self.settings_helper.in_defaults(name):
            self.settings_helper._raise_invalid_setting_name_error(name)
        return self.get_value_via_helper_method(name)

    def get_value_via_helper_method(self, setting_name):
        method = getattr(self.settings_helper, self.getter_method_name)
        return method(setting_name, warning_stacklevel=5)
