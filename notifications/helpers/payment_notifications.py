"""
Payment related notifications.
"""
from rest_framework.reverse import reverse
from notifications.models import Notification


def pay_later_reminder(payment, business_id, request, format=None):
    """
    Create a reminder notification for payments with
    mode of payments `CREDIT`.
    """
    customer_name = payment.order.customer.name
    action_url = reverse(
        'business:payment-detail',
        request=request,
        format=format,
        kwargs={'business_id': business_id, 'pk': payment.pk}
    )

    Notification.objects.get_or_create(
        notification_type='Payment Reminder',
        business_account=payment.order.business_account,
        action_message=f'Receive payment for your order to {customer_name}',
        action_date=payment.pay_later_date,
        action_date_label='Payment due date',
        action_url=action_url,
        is_seen=False
    )
