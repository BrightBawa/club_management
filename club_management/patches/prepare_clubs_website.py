import frappe

from club_management.utils.public_profiles import FORMATION_MESSAGE, WEBSITE_INTRODUCTION


def execute():
    """Prepare the website while club formation and profile publication are pending."""
    settings = frappe.get_single("Club Settings")
    changed = False
    for fieldname, value in (
        ("website_introduction", WEBSITE_INTRODUCTION),
        ("club_formation_message", FORMATION_MESSAGE),
        ("show_patron_directory", 1),
    ):
        # Newly added Check fields on an existing Single load as 0, even when
        # their schema default is 1. This one-time patch initializes that default.
        if settings.get(fieldname) is None or (
            fieldname == "show_patron_directory" and settings.get(fieldname) != 1
        ):
            settings.set(fieldname, value)
            changed = True
    if changed:
        settings.save(ignore_permissions=True)

    website = frappe.get_single("Website Settings")
    if not any((row.url or "").strip("/") == "clubs" for row in website.top_bar_items):
        item = website.append("top_bar_items", {"label": "Clubs", "url": "/clubs", "right": 1})
        sports_index = next(
            (i for i, row in enumerate(website.top_bar_items) if (row.url or "").strip("/") == "sports"),
            None,
        )
        if sports_index is not None:
            website.top_bar_items.remove(item)
            website.top_bar_items.insert(sports_index + 1, item)
        for index, row in enumerate(website.top_bar_items, 1):
            row.idx = index
        website.save(ignore_permissions=True)
