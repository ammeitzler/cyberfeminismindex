from django.contrib import admin

# Register your models here.
from wagtail.admin import widgets as wagtailadmin_widgets
from wagtail.core import hooks
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.menu import MenuItem
from django.urls import reverse



from django.db import models

from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel, PageChooserPanel, FieldRowPanel
