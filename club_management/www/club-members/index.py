import frappe

from club_management.utils.public_profiles import get_public_filters, selected_image, set_directory_context


def get_context(context):
    context.no_cache = 1
    context.title = "Club Members"
    set_directory_context(context)
    context.members = []
    if not context.member_profiles_enabled:
        return context
    rows = frappe.get_all(
        "Club Member Profile",
        filters=get_public_filters("Club Member Profile"),
        fields=["public_name", "route", "program", "student_group", "show_program", "show_student_group", "public_photo", "show_public_photo"],
        order_by="public_name asc",
    )
    context.members = [
        frappe._dict(
            public_name=row.public_name,
            route=row.route,
            program=row.program if row.show_program else None,
            student_group=row.student_group if row.show_student_group else None,
            profile_photo=selected_image(row, "public_photo"),
        )
        for row in rows
    ]
    return context
