import frappe

from club_management.utils.document_helpers import (
    get_student_display_name,
    make_unique_name,
    set_route,
    set_unique_slug,
    sync_published_on,
    validate_publication_state,
    validate_required_fields_for_publication,
)
from club_management.website_context import PublicWebsiteGenerator


class ClubMemberProfile(PublicWebsiteGenerator):
    website = frappe._dict(
        page_title_field="public_name",
        condition_field="publish_member_profile",
        template="templates/generators/club_member_profile.html",
        no_cache=1,
    )
    website_publish_field = "publish_member_profile"

    def autoname(self):
        self.public_name = self.public_name or get_student_display_name(self.student)
        self.name = make_unique_name(self.doctype, self.public_name or self.student, self.name)

    def validate(self):
        self.public_name = self.public_name or get_student_display_name(self.student)
        set_unique_slug(self, self.public_name or self.student)
        set_route(self, f"club-members/{self.slug}")
        sync_published_on(self, "publish_member_profile")
        validate_publication_state(self, "publish_member_profile")
        validate_required_fields_for_publication(
            self,
            "publish_member_profile",
            required_fields=("route", "public_photo"),
            require_one_of=("biography", "interests", "skills"),
        )

    def get_context(self, context):
        context.no_cache = 1
        context.title = self.public_name
        context.parents = [{"name": "Club Members", "route": "/club-members"}]
        return context
