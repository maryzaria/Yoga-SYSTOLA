import logging

from django.conf import settings

from .odoo import _jsonrpc, _authenticate

logger = logging.getLogger(__name__)


def is_email_allowed(email):
    tag = getattr(settings, "ODOO_ALLOW_TAG", "SYSTOLA_ALLOWED")
    if not tag:
        return True

    try:
        uid = _authenticate()
        if not uid:
            return False
        email = (email or "").strip().lower()

        tag_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    settings.ODOO_DB,
                    uid,
                    settings.ODOO_API_KEY,
                    "res.partner.category",
                    "search",
                    [[["name", "ilike", tag]]],
                    {"limit": 1},
                ],
            },
            "id": 1,
        }
        tag_ids = _jsonrpc(f"{settings.ODOO_URL}/jsonrpc", tag_payload)
        if not tag_ids:
            return False

        partner_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    settings.ODOO_DB,
                    uid,
                    settings.ODOO_API_KEY,
                    "res.partner",
                    "search_count",
                    [[["email", "ilike", email], ["category_id", "in", tag_ids]]],
                ],
            },
            "id": 2,
        }
        count = _jsonrpc(f"{settings.ODOO_URL}/jsonrpc", partner_payload)
        return bool(count)
    except Exception as exc:
        logger.warning("Odoo allowlist check failed: %s", exc)
        return False
