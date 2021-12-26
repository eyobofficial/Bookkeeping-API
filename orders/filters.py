import pendulum

from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Order


class OrderFilter(filters.FilterSet):
    customer = filters.CharFilter(method='customer_filter')
    type = filters.CharFilter(field_name='order_type', lookup_expr='iexact')
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    date = filters.CharFilter(field_name='created_at', lookup_expr='date')
    search = filters.CharFilter(method='search_filter')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')

    class Meta:
        model = Order
        fields = ['customer', 'description', 'type', 'status', 'date']

    def customer_filter(self, queryset, _, value):
        return queryset.filter(Q(customer__name__icontains=value) |
                               Q(customer__phone_number__icontains=value) |
                               Q(customer__email__icontains=value))

    def search_filter(self, queryset, _, value):
        try:
            pendulum.parse(value)
            return queryset.filter(created_at__date=value)
        except pendulum.exceptions.ParserError:
            return queryset.filter(Q(customer__name__icontains=value) |
                                   Q(customer__phone_number__icontains=value) |
                                   Q(customer__email__icontains=value) |
                                   Q(description__icontains=value))
