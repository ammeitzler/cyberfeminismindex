# from django.db import models
# from django.template.response import TemplateResponse

# from wagtail.core.models import Page
# from wagtail.core.fields import RichTextField
# from wagtail.admin.edit_handlers import FieldPanel
# from wagtailmarkdown.fields import MarkdownField

# import simplejson as json

# from index.models import IndexDetailPage

# class SearchPage(Page):
#     print("search")
#     def get_context(self, request, *args, **kwargs):
#     	context = []
#     	context["posts"] = IndexDetailPage.objects.live().public()
#     	json_list = list(context["posts"].values('slug', 'rownum', 'title'))
#     	context['json_dict'] = json.dumps(json_list)
#     	return context