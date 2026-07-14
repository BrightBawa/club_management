from __future__ import annotations

import re

import frappe
from frappe import _
from frappe.utils import cstr, getdate, now_datetime


def slugify(value: str | None) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return slug or frappe.generate_hash(length=8)


def record_exists(
    doctype: str, fieldname: str, value: str | None, current_name: str | None = None
) -> bool:
    if not value:
        return False

    filters = [[fieldname, "=", value]]
    if current_name:
        filters.append(["name", "!=", current_name])

    return bool(frappe.get_all(doctype, filters=filters, limit=1, pluck="name"))


def make_unique_value(
    doctype: str, fieldname: str, base_value: str | None, current_name: str | None = None
) -> str:
    base_value = str(base_value or "").strip() or frappe.generate_hash(length=8)
    candidate = base_value
    counter = 2

    while record_exists(doctype, fieldname, candidate, current_name):
        candidate = f"{base_value}-{counter}"
        counter += 1

    return candidate


def make_unique_name(doctype: str, base_value: str | None, current_name: str | None = None) -> str:
    return make_unique_value(doctype, "name", base_value, current_name)


def set_unique_slug(doc, source_value: str | None):
    if not doc.meta.get_field("slug"):
        return

    base_slug = slugify(source_value or doc.name)
    doc.slug = make_unique_value(doc.doctype, "slug", base_slug, doc.name)


def set_route(doc, route: str):
    if doc.meta.get_field("route"):
        doc.route = route.strip("/")


def sync_published_on(
    doc,
    publish_flag_field: str,
    status_field: str = "profile_status",
    published_on_field: str = "published_on",
):
    if not doc.meta.get_field(published_on_field):
        return

    is_published = bool(doc.get(publish_flag_field))
    if status_field and doc.meta.get_field(status_field):
        is_published = is_published and doc.get(status_field) == "Published"

    if is_published and not doc.get(published_on_field):
        doc.set(published_on_field, now_datetime())
    elif not is_published:
        doc.set(published_on_field, None)


def validate_publication_state(
    doc, publish_flag_field: str, status_field: str = "profile_status"
):
    if not doc.meta.get_field(status_field):
        return

    if doc.get(status_field) == "Published" and not doc.get(publish_flag_field):
        label = doc.meta.get_label(publish_flag_field) or publish_flag_field
        frappe.throw(_("Enable {0} before publishing this record.").format(label))


def validate_required_fields_for_publication(
    doc,
    publish_flag_field: str,
    status_field: str = "profile_status",
    required_fields: tuple[str, ...] | list[str] = (),
    require_one_of: tuple[str, ...] | list[str] = (),
):
    is_published = bool(doc.get(publish_flag_field))
    if status_field and doc.meta.get_field(status_field):
        is_published = is_published and doc.get(status_field) == "Published"

    if not is_published:
        return

    missing_labels = []
    for fieldname in required_fields:
        if not doc.meta.get_field(fieldname):
            continue

        value = doc.get(fieldname)
        if isinstance(value, str):
            value = cstr(value).strip()

        if not value:
            missing_labels.append(doc.meta.get_label(fieldname) or fieldname)

    if missing_labels:
        frappe.throw(
            _("The following fields are required before this record can be published: {0}").format(
                ", ".join(missing_labels)
            )
        )

    if require_one_of:
        for fieldname in require_one_of:
            if not doc.meta.get_field(fieldname):
                continue

            value = doc.get(fieldname)
            if isinstance(value, str):
                value = cstr(value).strip()

            if value:
                return

        labels = [doc.meta.get_label(fieldname) or fieldname for fieldname in require_one_of]
        frappe.throw(
            _("Add at least one public summary before publishing this record: {0}").format(
                ", ".join(labels)
            )
        )


def validate_date_range(doc, from_field: str, to_field: str, label: str):
    start_date = doc.get(from_field)
    end_date = doc.get(to_field)
    if start_date and end_date and getdate(start_date) > getdate(end_date):
        frappe.throw(_("{0} start date cannot be after the end date.").format(label))


def get_student_display_name(student: str | None) -> str:
    if not student:
        return ""

    student_row = frappe.db.get_value(
        "Student", student, ["student_name", "first_name", "last_name"], as_dict=True
    )
    if not student_row:
        return ""

    if student_row.student_name:
        return student_row.student_name

    return " ".join(filter(None, [student_row.first_name, student_row.last_name])).strip()


def get_employee_display_name(employee: str | None) -> str:
    if not employee:
        return ""

    return frappe.db.get_value("Employee", employee, "employee_name") or employee
