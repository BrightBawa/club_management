import frappe
from frappe import _

from club_management.utils.document_helpers import (
    make_unique_name,
    set_route,
    set_unique_slug,
    sync_published_on,
    validate_publication_state,
    validate_required_fields_for_publication,
)
from club_management.utils.public_profiles import (
    get_public_club_members,
    get_public_details,
    get_public_profile,
    selected_image,
    validate_optional_public_images,
)
from club_management.website_context import PublicWebsiteGenerator


class SchoolClub(PublicWebsiteGenerator):
    website = frappe._dict(
        page_title_field="club_name",
        condition_field="show_on_website",
        template="templates/generators/school_club.html",
        no_cache=1,
    )
    website_publish_field = "show_on_website"

    def autoname(self):
        self.name = make_unique_name(self.doctype, self.club_name, self.name)

    def validate(self):
        if self.show_on_website and self.profile_status == "Published" and self.status != "Active":
            frappe.throw(_("Set the club status to Active before publishing its profile."))
        set_unique_slug(self, self.club_name)
        set_route(self, f"clubs/{self.slug}")
        sync_published_on(self, "show_on_website")
        validate_publication_state(self, "show_on_website")
        validate_required_fields_for_publication(
            self,
            "show_on_website",
            required_fields=("route",),
            require_one_of=("description", "mission"),
        )
        validate_optional_public_images(self, ("logo", "cover_photo"))

    def website_extra_public_check(self):
        return self.status == "Active"

    def get_context(self, context):
        context.no_cache = 1
        context.title = self.club_name
        context.parents = [{"name": "Clubs", "route": "/clubs"}]
        context.public_details = get_public_details(self)
        context.club_logo = selected_image(self, "logo")
        context.cover_photo = selected_image(self, "cover_photo")
        context.category = self.club_category if self.get("show_club_category") else None
        for fieldname, doctype, title_field, label in (
            ("patron", "Club Patron Profile", "public_name", "Club patron"),
            ("student_president", "Club Member Profile", "public_name", "Student president"),
        ):
            if self.get(f"show_{fieldname}") and self.get(fieldname):
                row = get_public_profile(doctype, self.get(fieldname), [title_field, "route"])
                if row:
                    context.public_details.append(frappe._dict(label=_(label), value=row[title_field], route=row.route))
        context.members = get_public_club_members(self)
        return context
