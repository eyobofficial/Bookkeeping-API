from django_filters import rest_framework as filters

from orders.models import Order


class OrderFilter(filters.FilterSet):
    customer = filters.CharFilter(field_name='customer__name',
                                  lookup_expr='icontains')
    description = filters.CharFilter(field_name='description',
                                     lookup_expr='icontains')
    type = filters.CharFilter(field_name='order_type', lookup_expr='iexact')
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    date = filters.CharFilter(field_name='created_at', lookup_expr='date')

    class Meta:
        model = Order
        fields = ['customer', 'description', 'type', 'status', 'date']
