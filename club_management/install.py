import frappe


ROLE_NAMES = (
    "Clubs Manager",
    "Club Administrator",
    "Club Patron",
    "Assistant Club Patron",
    "Club Executive",
    "Club Member",
    "Club Content Editor",
    "Activities Coordinator",
    "Clubs Viewer",
)


def ensure_roles():
    for role_name in ROLE_NAMES:
        if frappe.db.exists("Role", role_name):
            continue
        frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(
            ignore_permissions=True
        )


def setup_workspace():
    frappe.reload_doc("clubs", "workspace", "clubs")
    frappe.clear_cache()


def after_install():
    ensure_roles()
    setup_workspace()
    frappe.db.commit()


def after_migrate():
    ensure_roles()
    setup_workspace()
    frappe.db.commit()
