import requests
from django.conf import settings


def send_whatsapp_template(to, template_name, params=None, language_code="en_US"):
    """
    Generic WhatsApp template message sender.

    Args:
        to: Recipient phone number with country code (e.g. "96599123456")
        template_name: Approved WhatsApp template name
        params: List of text strings for template body placeholders
        language_code: Template language code (default: en_US)
    """
    if params is None:
        params = []

    url = f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    components = []
    if params:
        components = [
            {
                "type": "body",
                "parameters": [{"type": "text", "text": str(p)} for p in params],
            }
        ]

    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
            "components": components,
        },
    }

    response = requests.post(url, headers=headers, json=body)
    return response.json()


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


def send_custom_text(to, message):
    """
    Send a free-form text message (only within 24-hour customer service window).
    """
    url = f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }
    response = requests.post(url, headers=headers, json=body)
    return response.json()