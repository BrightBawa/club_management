import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import frappe

from club_management.clubs.doctype.club_member_profile.club_member_profile import ClubMemberProfile
from club_management.patches.prepare_clubs_website import execute
from club_management.utils.public_profiles import (
    PUBLIC_DETAILS,
    get_current_memberships,
    get_public_club_members,
    get_public_details,
    get_public_filters,
    get_public_image_url,
    get_public_member_clubs,
    get_public_profile,
    selected_image,
    validate_optional_public_images,
)
from club_management.website_context import PublicWebsiteGenerator


class TestClubWebsiteOptions(unittest.TestCase):
    def setUp(self):
        translation = patch("club_management.utils.public_profiles._", side_effect=lambda value: value)
        translation.start()
        self.addCleanup(translation.stop)

    def test_every_optional_detail_requires_its_checkbox(self):
        for doctype, fields in PUBLIC_DETAILS.items():
            for fieldname, label in fields:
                with self.subTest(doctype=doctype, field=fieldname):
                    doc = frappe._dict(doctype=doctype, **{fieldname: "Internal detail"})
                    self.assertEqual(get_public_details(doc), [])
                    doc[f"show_{fieldname}"] = 1
                    self.assertEqual(get_public_details(doc)[0].value, "Internal detail")
                    doc[f"show_{fieldname}"] = "0"
                    self.assertEqual(get_public_details(doc), [])

    def test_empty_details_and_internal_identifiers_are_omitted(self):
        for value in (None, "", "   "):
            doc = frappe._dict(doctype="Club Member Profile", skills=value, show_skills=1,
                               student="PRIVATE-STUDENT-ID", show_student=1)
            self.assertEqual(get_public_details(doc), [])

    def test_photos_require_a_checkbox_and_a_public_url(self):
        doc = frappe._dict(public_photo="/files/photo.jpg")
        self.assertIsNone(selected_image(doc, "public_photo"))
        doc.show_public_photo = 1
        self.assertEqual(selected_image(doc, "public_photo"), "/files/photo.jpg")
        for url in ("/private/files/photo.jpg", "/%70rivate/files/photo.jpg",
                    "https://school.example/private/files/photo.jpg", "javascript:alert(1)", "https://[invalid"):
            with self.subTest(url=url):
                self.assertIsNone(get_public_image_url(url))

    def test_private_selected_photo_blocks_publication(self):
        values = {"photograph": "/private/files/photo.jpg", "show_photograph": 1}
        doc = SimpleNamespace(get=values.get, is_website_published=lambda: True,
                              meta=SimpleNamespace(get_label=lambda field: "Photograph"))
        with patch("club_management.utils.public_profiles.frappe.throw", side_effect=frappe.ValidationError):
            with self.assertRaises(frappe.ValidationError):
                validate_optional_public_images(doc, ("photograph",))
        values["show_photograph"] = 0
        validate_optional_public_images(doc, ("photograph",))

    def test_public_clubs_require_active_and_published_states(self):
        filters = get_public_filters("School Club")
        self.assertEqual(filters, {"show_on_website":1, "profile_status":"Published", "status":"Active"})

    def test_global_member_disable_prevents_related_profile_lookups(self):
        db = MagicMock()
        with patch("club_management.utils.public_profiles.member_profiles_enabled", return_value=False), \
             patch("club_management.utils.public_profiles.frappe.db", new=db):
            self.assertIsNone(get_public_profile("Club Member Profile", "Member", ["public_name", "route"]))
            db.get_value.assert_not_called()

    def test_member_profile_requires_global_enable_and_public_visibility(self):
        doc = frappe._dict(profile_visibility="Internal Only", membership_status="Active")
        target = "club_management.clubs.doctype.club_member_profile.club_member_profile.member_profiles_enabled"
        with patch(target, return_value=True):
            self.assertFalse(ClubMemberProfile.website_extra_public_check(doc))
            doc.profile_visibility = "Public Summary"
            self.assertTrue(ClubMemberProfile.website_extra_public_check(doc))
            doc.membership_status = "Inactive"
            self.assertFalse(ClubMemberProfile.website_extra_public_check(doc))
        doc.membership_status = "Active"
        with patch(target, return_value=False):
            self.assertFalse(ClubMemberProfile.website_extra_public_check(doc))

    def test_guest_cannot_render_an_unpublished_route(self):
        doc = SimpleNamespace(is_website_published=lambda: False, has_permission=MagicMock())
        with patch("club_management.website_context.frappe.session", new=SimpleNamespace(user="Guest")):
            with self.assertRaises(frappe.DoesNotExistError):
                PublicWebsiteGenerator.get_page_info(doc)
        doc.has_permission.assert_not_called()

    def test_disabled_rosters_and_memberships_are_not_queried(self):
        with patch("club_management.utils.public_profiles.frappe.get_all") as query:
            self.assertEqual(get_public_club_members(frappe._dict(name="Club", show_members=0)), [])
            self.assertEqual(get_public_member_clubs(frappe._dict(name="Member", show_memberships=0)), [])
            query.assert_not_called()
        with patch("club_management.utils.public_profiles.member_profiles_enabled", return_value=False), \
             patch("club_management.utils.public_profiles.frappe.get_all") as query:
            self.assertEqual(get_public_club_members(frappe._dict(name="Club", show_members=1)), [])
            query.assert_not_called()

    def test_roster_requires_public_member_opt_in_and_hides_unticked_roles(self):
        memberships = [frappe._dict(member_profile="Member", position="President")]
        rows = [frappe._dict(name="Member", public_name="Public member", route="club-members/member", show_membership_roles=0)]
        with patch("club_management.utils.public_profiles.member_profiles_enabled", return_value=True), \
             patch("club_management.utils.public_profiles.get_current_memberships", return_value=memberships), \
             patch("club_management.utils.public_profiles.frappe.get_all", return_value=rows) as query:
            result = get_public_club_members(frappe._dict(name="Club", show_members=1))
            self.assertIsNone(result[0].position)
            filters = query.call_args.kwargs["filters"]
            self.assertEqual(filters["show_memberships"], 1)
            self.assertEqual(filters["publish_member_profile"], 1)
            self.assertEqual(filters["profile_status"], "Published")
            self.assertEqual(filters["membership_status"], "Active")
            self.assertIn("Public Summary", filters["profile_visibility"][1])

    def test_membership_queries_require_current_active_approved_records(self):
        with patch("club_management.utils.public_profiles.frappe.get_all", return_value=[]) as query:
            get_current_memberships({"club":"Club"}, ["member_profile"])
            self.assertEqual(query.call_args.kwargs["filters"], {
                "club":"Club", "is_current":1, "application_status":"Approved", "membership_status":"Active",
            })

    def test_website_preparation_is_idempotent_and_preserves_member_disable(self):
        values = {"public_member_profiles_enabled":0, "show_patron_directory":0}
        settings = SimpleNamespace(get=values.get, set=values.__setitem__, save=MagicMock())
        items = [frappe._dict(label="Sports", url="/sports", right=1),
                 frappe._dict(label="Incident", url=None, right=1)]
        def append(fieldname, value):
            item = frappe._dict(value)
            items.append(item)
            return item
        website = SimpleNamespace(top_bar_items=items, append=append, save=MagicMock())
        with patch("club_management.patches.prepare_clubs_website.frappe.get_single",
                   side_effect=lambda dt: settings if dt=="Club Settings" else website):
            execute()
            execute()
        self.assertEqual([row.label for row in items], ["Sports", "Clubs", "Incident"])
        self.assertEqual(values["public_member_profiles_enabled"], 0)
        self.assertEqual(values["show_patron_directory"], 1)
        website.save.assert_called_once()
        settings.save.assert_called_once()
