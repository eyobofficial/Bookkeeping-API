from django.shortcuts import get_object_or_404


class BaseBusinessAccountDetailViewSet:
    """
    Base view class for business account detail viewsets.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        business_id = self.kwargs.get('business_id')
        return qs.filter(business_account__id=business_id)

    def get_business_account(self):
        """
        Return the current active business account.
        """
        business_id = self.kwargs.get('business_id')
        user_business_accounts = self.request.user.business_accounts.all()
        return get_object_or_404(user_business_accounts, pk=business_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['business_account'] = self.get_business_account()
        return context

    def perform_create(self, serializer):
        """
        Attach the current business account to created resource.
        """
        business_account = self.get_business_account()
        serializer.save(business_account=business_account)
