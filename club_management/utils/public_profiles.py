from urllib.parse import unquote, urlsplit

import frappe
from frappe import _
from frappe.utils import cint


FORMATION_MESSAGE = "Club formation is pending. Approved clubs and activities will appear here once they are ready."
WEBSITE_INTRODUCTION = "Explore opportunities to develop interests, talents, leadership, and service through school clubs and activities."
PUBLIC_MEMBER_VISIBILITIES = ("Public Summary", "Fully Published")

PUBLIC_DETAILS = {
    "School Club": (
        ("club_motto", "Club motto"),
        ("mission", "Mission"),
        ("objectives", "Objectives"),
        ("activities_summary", "Activities and projects"),
        ("achievements_summary", "Club achievements"),
        ("membership_requirements", "Membership requirements"),
        ("campus", "Campus"),
        ("academic_year", "Academic year"),
        ("meeting_venue", "Meeting venue"),
        ("meeting_schedule", "Meeting schedule"),
        ("max_membership", "Membership capacity"),
    ),
    "Club Patron Profile": (
        ("clubs_supervised", "Clubs supervised"),
        ("relevant_skills", "Relevant skills"),
        ("qualifications", "Professional qualifications"),
        ("experience", "Mentoring experience"),
        ("mentoring_approach", "Mentoring approach"),
        ("achievements_summary", "Achievements"),
        ("languages", "Languages"),
    ),
    "Club Member Profile": (
        ("program", "Program"),
        ("student_group", "Student group"),
        ("campus", "Campus"),
        ("interests", "Interests"),
        ("skills", "Skills"),
        ("achievements_summary", "Achievements"),
        ("personal_goals", "Personal goals"),
        ("contribution_summary", "Club contributions"),
    ),
}


def member_profiles_enabled():
    return bool(cint(frappe.db.get_single_value("Club Settings", "public_member_profiles_enabled")))


def get_public_filters(doctype):
    filters = {
        "School Club": {"show_on_website": 1, "profile_status": "Published", "status": "Active"},
        "Club Patron Profile": {"publish_patron_profile": 1, "profile_status": "Published"},
        "Club Member Profile": {
            "publish_member_profile": 1,
            "profile_status": "Published",
            "profile_visibility": ["in", PUBLIC_MEMBER_VISIBILITIES],
            "membership_status": "Active",
        },
    }
    return filters[doctype]


def get_public_profile(doctype, name, fields):
    if not name or (doctype == "Club Member Profile" and not member_profiles_enabled()):
        return None
    return frappe.db.get_value(doctype, {"name": name, **get_public_filters(doctype)}, fields, as_dict=True)


def get_public_details(doc):
    details = []
    for fieldname, label in PUBLIC_DETAILS.get(doc.doctype, ()):
        value = doc.get(fieldname)
        if cint(doc.get(f"show_{fieldname}")) and value and str(value).strip():
            details.append(frappe._dict(label=_(label), value=value, route=None))
    return details


def get_public_image_url(value):
    if not value:
        return None
    try:
        parts = urlsplit(value)
    except ValueError:
        return None
    path = unquote(parts.path)
    if path.startswith("/private/"):
        return None
    if (parts.scheme in ("http", "https") and parts.netloc) or (
        not parts.scheme and not parts.netloc and path.startswith(("/files/", "/assets/"))
    ):
        return value
    return None


def selected_image(doc, fieldname):
    return get_public_image_url(doc.get(fieldname)) if cint(doc.get(f"show_{fieldname}")) else None


def validate_optional_public_images(doc, fieldnames):
    if not doc.is_website_published():
        return
    for fieldname in fieldnames:
        value = doc.get(fieldname)
        if value and cint(doc.get(f"show_{fieldname}")) and not get_public_image_url(value):
            frappe.throw(
                _("{0} must be a public image to display on the website. Upload a public image or untick its display option.").format(doc.meta.get_label(fieldname))
            )


def get_current_memberships(filters, fields):
    return frappe.get_all(
        "Club Membership",
        filters={"is_current": 1, "application_status": "Approved", "membership_status": "Active", **filters},
        fields=fields,
        order_by="modified desc",
    )


def get_public_club_members(club):
    if not cint(club.get("show_members")) or not member_profiles_enabled():
        return []
    memberships = get_current_memberships({"club": club.name}, ["member_profile", "position"])
    if not memberships:
        return []
    positions = {}
    for membership in memberships:
        positions.setdefault(membership.member_profile, membership.position)
    rows = frappe.get_all(
        "Club Member Profile",
        filters={**get_public_filters("Club Member Profile"), "name": ["in", list(positions)], "show_memberships": 1},
        fields=["name", "public_name", "route", "show_membership_roles"],
        order_by="public_name asc",
    )
    for row in rows:
        row.position = positions[row.name] if cint(row.show_membership_roles) else None
    return rows


def get_public_member_clubs(member):
    if not cint(member.get("show_memberships")) or not member_profiles_enabled():
        return []
    memberships = get_current_memberships({"member_profile": member.name}, ["club", "position"])
    if not memberships:
        return []
    positions = {}
    for membership in memberships:
        positions.setdefault(membership.club, membership.position)
    rows = frappe.get_all(
        "School Club",
        filters={**get_public_filters("School Club"), "name": ["in", list(positions)], "show_members": 1},
        fields=["name", "club_name", "route"],
        order_by="club_name asc",
    )
    for row in rows:
        row.position = positions[row.name] if cint(member.get("show_membership_roles")) else None
    return rows


def get_public_patron_clubs(patron):
    if not cint(patron.get("show_clubs_supervised")):
        return []
    return frappe.get_all(
        "School Club",
        filters={**get_public_filters("School Club"), "patron": patron.name, "show_patron": 1},
        fields=["club_name", "route"],
        order_by="club_name asc",
    )


def set_directory_context(context):
    settings = frappe.get_single("Club Settings")
    context.website_introduction = settings.get("website_introduction") or _(WEBSITE_INTRODUCTION)
    context.club_formation_message = settings.get("club_formation_message") or _(FORMATION_MESSAGE)
    show_patrons = settings.get("show_patron_directory")
    context.show_patron_directory = bool(cint(show_patrons)) if show_patrons is not None else True
    context.member_profiles_enabled = bool(cint(settings.get("public_member_profiles_enabled")))
    return context
