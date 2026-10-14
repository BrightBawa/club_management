import frappe

from club_management.utils.public_profiles import get_public_filters, selected_image, set_directory_context


def get_context(context):
    context.no_cache = 1
    context.title = "Clubs"
    set_directory_context(context)
    rows = frappe.get_all(
        "School Club",
        filters=get_public_filters("School Club"),
        fields=["club_name", "route", "club_category", "description", "logo", "cover_photo", "show_club_category", "show_logo", "show_cover_photo"],
        order_by="club_name asc",
    )
    context.clubs = [
        frappe._dict(
            club_name=row.club_name,
            route=row.route,
            description=row.description,
            category=row.club_category if row.show_club_category else None,
            logo=selected_image(row, "logo"),
            cover_photo=selected_image(row, "cover_photo"),
        )
        for row in rows
    ]
    return context
