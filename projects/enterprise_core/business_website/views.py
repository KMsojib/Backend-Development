from rest_framework import viewsets
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import WebPage # Standard flat page schema model
from .serializers import WebPageSerializer

class PublicWebPageViewSet(viewsets.ModelViewSet):
    queryset = WebPage.objects.all()
    serializer_class = WebPageSerializer
    lookup_field = 'slug'

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)