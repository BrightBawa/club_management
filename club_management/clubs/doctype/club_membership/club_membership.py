import frappe
from frappe import _
from frappe.model.document import Document

from club_management.utils.document_helpers import validate_date_range


class ClubMembership(Document):
    def validate(self):
        validate_date_range(self, "date_joined", "date_exited", _("Club membership"))
        self.validate_duplicate_membership()

    def validate_duplicate_membership(self):
        existing = frappe.get_all(
            "Club Membership",
            filters=[
                ["club", "=", self.club],
                ["member_profile", "=", self.member_profile],
                ["academic_year", "=", self.academic_year],
                ["academic_term", "=", self.academic_term],
                ["name", "!=", self.name],
            ],
            limit=1,
            pluck="name",
        )
        if existing:
            frappe.throw(_("This member already has a membership for the same club and period."))
