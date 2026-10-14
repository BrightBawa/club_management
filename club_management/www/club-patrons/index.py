import frappe

from club_management.utils.public_profiles import get_public_filters, selected_image, set_directory_context


def get_context(context):
    context.no_cache = 1
    context.title = "Club Patrons"
    set_directory_context(context)
    context.patrons = []
    if not context.show_patron_directory:
        return context
    rows = frappe.get_all(
        "Club Patron Profile",
        filters=get_public_filters("Club Patron Profile"),
        fields=["public_name", "route", "clubs_supervised", "show_clubs_supervised", "designation", "show_designation", "photograph", "show_photograph"],
        order_by="public_name asc",
    )
    context.patrons = [
        frappe._dict(
            public_name=row.public_name,
            route=row.route,
            clubs_supervised=row.clubs_supervised if row.show_clubs_supervised else None,
            designation=row.designation if row.show_designation else None,
            profile_photo=selected_image(row, "photograph"),
        )
        for row in rows
    ]
    return context
