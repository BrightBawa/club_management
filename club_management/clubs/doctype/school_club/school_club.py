import frappe

from club_management.utils.document_helpers import (
    make_unique_name,
    set_route,
    set_unique_slug,
    sync_published_on,
    validate_publication_state,
    validate_required_fields_for_publication,
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

    def get_context(self, context):
        context.no_cache = 1
        context.title = self.club_name
        context.parents = [{"name": "Clubs", "route": "/clubs"}]
        return context
