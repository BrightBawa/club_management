import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Clubs"
    context.clubs = frappe.get_all(
        "School Club",
        filters={"show_on_website": 1, "profile_status": "Published"},
        fields=["club_name", "route", "club_category", "description"],
        order_by="club_name asc",
    )
    return context
