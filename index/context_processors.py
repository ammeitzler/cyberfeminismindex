def add_index_to_context(request):
	from index.models import IndexDetailPage

	return {
        'index_context': IndexDetailPage.objects.live().public()
    }

def add_collections_to_context(request):
	from index.models import IndexCurators

	return {
        'index_collections': IndexCurators.objects.all()
    }

def add_viewdownloads_to_context(request):
	from index.models import IndexDownloads

	return {
        'index_viewdownloads': IndexDownloads.objects.all()
    }