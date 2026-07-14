import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Club Members"
    context.members = frappe.get_all(
        "Club Member Profile",
        filters={"publish_member_profile": 1, "profile_status": "Published"},
        fields=["public_name", "route", "program", "student_group"],
        order_by="public_name asc",
    )
    return context
