import frappe
from frappe import _

from club_management.utils.document_helpers import (
    get_employee_display_name,
    make_unique_name,
    set_route,
    set_unique_slug,
    sync_published_on,
    validate_publication_state,
    validate_required_fields_for_publication,
)
from club_management.website_context import PublicWebsiteGenerator


class ClubPatronProfile(PublicWebsiteGenerator):
    website = frappe._dict(
        page_title_field="public_name",
        condition_field="publish_patron_profile",
        template="templates/generators/club_patron_profile.html",
        no_cache=1,
    )
    website_publish_field = "publish_patron_profile"

    def autoname(self):
        self.public_name = self.public_name or get_employee_display_name(self.employee)
        self.name = make_unique_name(self.doctype, self.public_name or self.employee, self.name)

    def validate(self):
        if not self.employee and not self.public_name:
            frappe.throw(_("Club patron profiles require an Employee or Public Name."))

        self.public_name = self.public_name or get_employee_display_name(self.employee)
        set_unique_slug(self, self.public_name or self.employee)
        set_route(self, f"club-patrons/{self.slug}")
        sync_published_on(self, "publish_patron_profile")
        validate_publication_state(self, "publish_patron_profile")
        validate_required_fields_for_publication(
            self,
            "publish_patron_profile",
            required_fields=("route",),
            require_one_of=("biography", "relevant_skills"),
        )

    def get_context(self, context):
        context.no_cache = 1
        context.title = self.public_name
        context.parents = [{"name": "Club Patrons", "route": "/club-patrons"}]
        return context
