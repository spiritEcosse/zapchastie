from models import MetaTags
from django.core.exceptions import ObjectDoesNotExist


def meta_tags(request):
    context = {}

    try:
        meta_tags = MetaTags.objects.get(page_url=request.path)
    except ObjectDoesNotExist:
        pass
    else:
        context['meta_tags'] = meta_tags

    return context
