import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Club Patrons"
    context.patrons = frappe.get_all(
        "Club Patron Profile",
        filters={"publish_patron_profile": 1, "profile_status": "Published"},
        fields=["public_name", "route", "clubs_supervised"],
        order_by="public_name asc",
    )
    return context
