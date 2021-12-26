import pendulum

from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Payment


class SalesFilter(filters.FilterSet):
    customer = filters.CharFilter(method='customer_filter')
    date = filters.CharFilter(field_name='created_at', lookup_expr='date')
    search = filters.CharFilter(method='search_filter')
    modeOfPayment = filters.CharFilter(field_name='mode_of_payment', lookup_expr='iexact')

    class Meta:
        model = Payment
        fields = ['customer', 'date', 'search', 'modeOfPayment']

    def customer_filter(self, queryset, _, value):
        return queryset.filter(Q(order__customer__name__icontains=value) |
                               Q(order__customer__phone_number__icontains=value) |
                               Q(order__customer__email__icontains=value))

    def search_filter(self, queryset, _, value):
        try:
            pendulum.parse(value)
            return queryset.filter(created_at__date=value)
        except pendulum.exceptions.ParserError:
            return queryset.filter(Q(mode_of_payment__iexact=value) |
                                   Q(order__customer__name__icontains=value) |
                                   Q(order__customer__phone_number__icontains=value) |
                                   Q(order__customer__email__icontains=value) |
                                   Q(order__description__icontains=value))

