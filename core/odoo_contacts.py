import logging

from django.conf import settings

from .odoo import _authenticate, _jsonrpc

logger = logging.getLogger(__name__)


def fetch_contacts(limit=200):
    try:
        uid = _authenticate()
        if not uid:
            return []

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
                    "search_read",
                    [[["email", "!=", False]]],
                    {"fields": ["name", "email", "category_id"], "limit": limit},
                ],
            },
            "id": 1,
        }
        partners = _jsonrpc(f"{settings.ODOO_URL}/jsonrpc", partner_payload) or []

        tag_ids = set()
        for partner in partners:
            for tag_id in partner.get("category_id", []):
                tag_ids.add(tag_id)

        tag_map = {}
        if tag_ids:
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
                        "read",
                        [list(tag_ids)],
                        {"fields": ["name"]},
                    ],
                },
                "id": 2,
            }
            tags = _jsonrpc(f"{settings.ODOO_URL}/jsonrpc", tag_payload) or []
            tag_map = {tag["id"]: tag["name"] for tag in tags if "id" in tag}

        results = []
        for partner in partners:
            tags = [tag_map.get(tid, str(tid)) for tid in partner.get("category_id", [])]
            results.append(
                {
                    "name": partner.get("name") or "",
                    "email": partner.get("email") or "",
                    "tags": tags,
                }
            )
        return results
    except Exception as exc:
        logger.warning("Odoo contacts fetch failed: %s", exc)
        return []
