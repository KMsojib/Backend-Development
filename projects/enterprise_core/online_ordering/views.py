from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from .models import Cart, Storefront
from .serializers import CartSerializer

class CustomerCartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        domain = self.request.META.get('HTTP_X_STOREFRONT_DOMAIN')
        return Cart.objects.filter(storefront__domain_name=domain)

    def perform_create(self, serializer):
        domain = self.request.META.get('HTTP_X_STOREFRONT_DOMAIN')
        try:
            storefront = Storefront.objects.get(domain_name=domain)
        except Storefront.DoesNotExist:
            raise ValidationError("Invalid or missing X-Storefront-Domain header.")

        serializer.save(user=self.request.user, storefront=storefront)