from frappe import _


def get_data():
    return [
        {
            "module_name": "Clubs",
            "category": "Modules",
            "label": _("Clubs & Activities"),
            "type": "module",
            "description": _("Clubs, member profiles, patrons, memberships, and activities."),
        }
    ]
