import requests
from django.conf import settings

def send_whatsapp_template(to, template_name, params=[]):
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
                "parameters": [{"type": "text", "text": p} for p in params],
            }
        ]

    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en_US"},
            "components": components,
        },
    }

    response = requests.post(url, headers=headers, json=body)
    return response.json()