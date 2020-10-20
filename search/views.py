from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from wagtail.core.models import Page
from wagtail.search.models import Query

from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.shortcuts import render

from index.models import IndexDetailPage, IndexCategory, IndexDownloads

from django.template.loader import render_to_string
from django.http import JsonResponse
from wagtail.search import index

import simplejson as json

def get_json(x):
    context = dict()
    context["posts"] = IndexDetailPage.objects.live().public()
    json_list = list(context["posts"].values('slug', 'rownum', 'title', 'author_founder','pub_date','end_date', 'about', 'location', 'external_link', 'external_link_two', 'images_list','page_ptr_id', 'page_ptr_id'))
    json_dict = json.dumps(json_list)
    context["image_entries"] = []

    for index in context["posts"]:
       for c in index.images_list.all():
          context["image_entries"].append({"slug":index.slug, "img_name":str(c)})

    json_img_dict = json.dumps(list(context["image_entries"]))
    
    if x == 1:
        return json_dict
    else:
        return json_img_dict

def autocomplete_search(request):
    search_categories = IndexCategory.objects.all()

    if request.is_ajax():
        search_query = request.GET.get('q', None)
        search_results_ajax = IndexDetailPage.objects.live().search(search_query)

        json_dict = get_json(1)
        json_img_dict = get_json(2)
        
        html = render_to_string(
            template_name="search/search-results-partial.html", 
            context={
            "search_query": search_query, 
            "search_results": None, 
            "search_results_ajax": search_results_ajax,
            "search_categories": search_categories, 
            "json_dict": json_dict,
            'json_img_dict': json_img_dict,}
        )
        data_dict = {"html_from_view": html}

        return JsonResponse(data=data_dict, safe=False)


def search(request):
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    search_categories = IndexCategory.objects.all()

    # Search
    if search_query:
        search_results = IndexDetailPage.objects.live().search(search_query)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = IndexDetailPage.objects.none()

    json_dict = get_json(1)
    json_img_dict = get_json(2)

    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
        'search_categories': search_categories,
        'json_dict': json_dict,
        'json_img_dict': json_img_dict,
    })
