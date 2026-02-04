import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _jsonrpc(url, payload):
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()
    data = response.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("result")


def _authenticate():
    if not settings.ODOO_API_KEY:
        raise RuntimeError("ODOO_API_KEY is not set")
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "authenticate",
            "args": [
                settings.ODOO_DB,
                settings.ODOO_LOGIN,
                settings.ODOO_API_KEY,
                {},
            ],
        },
        "id": 1,
    }
    return _jsonrpc(f"{settings.ODOO_URL}/jsonrpc", payload)


def create_lead(name, email=None, description=None, phone=None):
    try:
        uid = _authenticate()
        if not uid:
            raise RuntimeError("Authentication failed")
        values = {"name": name}
        if email:
            values["email_from"] = email
        if description:
            values["description"] = description
        if phone:
            values["phone"] = phone

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    settings.ODOO_DB,
                    uid,
                    settings.ODOO_API_KEY,
                    "crm.lead",
                    "create",
                    [values],
                ],
            },
            "id": 2,
        }
        return _jsonrpc(f"{settings.ODOO_URL}/jsonrpc", payload)
    except Exception as exc:
        logger.warning("Odoo lead creation failed: %s", exc)
        return None
