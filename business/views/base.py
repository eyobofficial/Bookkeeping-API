from django.shortcuts import get_object_or_404

from business.models import BusinessAccount


class BaseBusinessAccountDetailViewSet:
    """
    Base view class for business account detail viewsets.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        business_id = self.kwargs.get('business_id')
        return qs.filter(business_account__id=business_id)

    def perform_create(self, serializer):
        business_id = self.kwargs.get('business_id')
        business_account = get_object_or_404(BusinessAccount, pk=business_id)
        serializer.save(business_account=business_account)
