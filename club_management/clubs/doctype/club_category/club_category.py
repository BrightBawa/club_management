from frappe.model.document import Document

from club_management.utils.document_helpers import make_unique_name


class ClubCategory(Document):
    def autoname(self):
        self.name = make_unique_name(self.doctype, self.category_name, self.name)
