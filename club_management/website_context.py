from __future__ import annotations

import frappe
from frappe.utils import cstr
from frappe.website.website_generator import WebsiteGenerator


class PublicWebsiteGenerator(WebsiteGenerator):
    website = frappe._dict(no_cache=1)
    website_publish_field = ""
    website_status_field = "profile_status"

    def website_extra_public_check(self) -> bool:
        return True

    def is_website_published(self):
        if self.website_publish_field and not self.get(self.website_publish_field):
            return False

        if self.website_status_field and self.get(self.website_status_field) != "Published":
            return False

        return self.website_extra_public_check()

    def has_website_permission(self, ptype, user, verbose=False):
        if user == "Guest":
            return self.is_website_published()

        return self.has_permission(ptype=ptype, user=user, verbose=verbose)


def get_query_value(key: str, default: str = "") -> str:
    return cstr(frappe.form_dict.get(key) or default).strip()
