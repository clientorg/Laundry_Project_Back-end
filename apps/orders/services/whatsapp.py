import requests
from django.conf import settings


# ---------------------------------------------------------------------------
# MSG91 WhatsApp API
# Docs: https://docs.msg91.com/reference/whatsapp-send-template-message
# ---------------------------------------------------------------------------

MSG91_WHATSAPP_URL = "https://api.msg91.com/api/v5/whatsapp/whatsapp-outbound-message/bulk/"


def _get_whatsapp_number():
    from apps.master.models import AppSettings
    return AppSettings.get('whatsapp_number', default=settings.MSG91_WHATSAPP_NUMBER)


def _get_auth_key():
    from apps.master.models import AppSettings
    return AppSettings.get('msg91_auth_key', default=settings.MSG91_AUTH_KEY)


def _get_whatsapp_namespace():
    from apps.master.models import AppSettings
    return AppSettings.get('msg91_whatsapp_namespace', default=settings.MSG91_WHATSAPP_NAMESPACE)


def send_whatsapp_template(to, template_name, params=None, language_code="en"):
    """
    Send a WhatsApp template message via MSG91.

    Args:
        to:             Recipient phone number with country code (e.g. "96599123456")
        template_name:  Approved MSG91 / WhatsApp template name
        params:         List of text strings for template body placeholders (body_1, body_2, ...)
        language_code:  Template language code (default: "en")
    """
    if params is None:
        params = []

    headers = {
        "authkey": _get_auth_key(),
        "Content-Type": "application/json",
    }

    # Build components as body_1, body_2, ... keyed dict
    components = {
        f"body_{i + 1}": {"type": "text", "value": str(p)}
        for i, p in enumerate(params)
    }

    payload = {
        "integrated_number": _get_whatsapp_number(),
        "content_type": "template",
        "payload": {
            "messaging_product": "whatsapp",
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code,
                    "policy": "deterministic",
                },
                "namespace": _get_whatsapp_namespace(),
                "to_and_components": [
                    {
                        "to": [to],
                        "components": components,
                    }
                ],
            },
        },
    }

    response = requests.post(MSG91_WHATSAPP_URL, headers=headers, json=payload)
    try:
        return response.json()
    except Exception:
        return {"raw": response.text, "status_code": response.status_code}


# ---------------------------------------------------------------------------
# Notification helpers
# ---------------------------------------------------------------------------

def notify_order_ready(order):
    """Send 'order ready for pickup' notification."""
    phone = f"{order.customer.country_code}{order.customer.mobile_number}"
    return send_whatsapp_template(
        to=phone,
        template_name="order_ready",
        params=[order.customer.name or "", order.order_id],
    )


def notify_order_delivered(order):
    """Send 'order delivered' notification."""
    phone = f"{order.customer.country_code}{order.customer.mobile_number}"
    return send_whatsapp_template(
        to=phone,
        template_name="order_delivered",
        params=[order.customer.name or "", order.order_id],
    )


def notify_payment_received(order, amount):
    """Send payment confirmation notification."""
    phone = f"{order.customer.country_code}{order.customer.mobile_number}"
    return send_whatsapp_template(
        to=phone,
        template_name="payment_received",
        params=[order.customer.name or "", order.order_id, str(amount)],
    )


def notify_order_placement(customer_name, phone, voucher_number, status):
    """Send order placement confirmation via WhatsApp template."""
    return send_whatsapp_template(
        to=phone,
        template_name="laundry_new_order",
        params=[customer_name, voucher_number, status],
    )


def notify_order_status_update(customer_name, phone, voucher_number, status):
    """Send order status update notification via WhatsApp template."""
    return send_whatsapp_template(
        to=phone,
        template_name="laundry_status_update",
        params=[customer_name, voucher_number, status],
    )


def send_custom_text(to, message):
    """
    Send a free-form text message (only within 24-hour customer service window).
    Uses MSG91 WhatsApp text payload.
    """
    headers = {
        "authkey": _get_auth_key(),
        "Content-Type": "application/json",
    }

    payload = {
        "integrated_number": _get_whatsapp_number(),
        "content_type": "text",
        "payload": {
            "messaging_product": "whatsapp",
            "type": "text",
            "text": {"body": message},
            "to": to,
        },
    }

    response = requests.post(MSG91_WHATSAPP_URL, headers=headers, json=payload)
    try:
        return response.json()
    except Exception:
        return {"raw": response.text, "status_code": response.status_code}
