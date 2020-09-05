from django.contrib import admin
from django.contrib.admin import ModelAdmin
from index.models import IndexPage

# Register your models here.
class IndexAdmin(ModelAdmin):
   model = IndexPage
