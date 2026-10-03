"""Functional and security regression tests for recursive JSON searches."""

import unittest
from copy import deepcopy

from policy import POLICY
from recursive_json_search import json_search
from test_data import data, key1, key2


class json_search_test(unittest.TestCase):
    def test_search_found(self):
        """Find the exact issue summary in the supplied nested fixture."""
        self.assertEqual(
            json_search(key1, data, role="viewer"),
            ["Network Device 10.10.20.82 Is Unreachable From Controller"],
        )

    def test_search_not_found(self):
        """Return an empty list when the requested key does not exist."""
        self.assertEqual(json_search(key2, data, role="admin"), [])

    def test_is_a_list(self):
        """Always return a list for successful, missing, and denied searches."""
        for key, role in [(key1, "viewer"), (key2, "admin"), ("apiKey", "viewer")]:
            with self.subTest(key=key, role=role):
                self.assertIsInstance(json_search(key, data, role=role), list)

    def test_collects_all_nested_matches(self):
        """Aggregate sibling dictionaries and nested lists without losing matches."""
        source = [
            {"target": "first", "child": {"target": "second"}},
            [[{"target": "third"}], {"target": "fourth"}],
            {"target": "first"},
        ]
        self.assertEqual(
            json_search("target", source),
            ["first", "second", "third", "fourth", "first"],
        )

    def test_searches_inside_matched_containers(self):
        """Keep container values intact and also find matches nested inside them."""
        source = {"target": [{"target": {"target": "leaf"}}]}
        self.assertEqual(
            json_search("target", source),
            [[{"target": {"target": "leaf"}}], {"target": "leaf"}, "leaf"],
        )

    def test_preserves_falsey_values(self):
        """Keep null, false, zero, empty strings, and empty containers as matches."""
        values = [None, False, 0, "", [], {}]
        self.assertEqual(
            json_search("target", [{"target": value} for value in values]), values
        )

    def test_empty_and_scalar_inputs(self):
        """Ignore scalar inputs and return no matches from empty containers."""
        for source in [None, False, 0, "target", [], {}]:
            with self.subTest(source=source):
                self.assertEqual(json_search("target", source), [])

    def test_api_key_permissions(self):
        """SR-01: Only admins can read the fixture's API key."""
        for role in ["admin", "operator", "viewer"]:
            with self.subTest(role=role):
                expected = ["SNMP-COMMUNITY-STRING-7f3a9c"] if role == "admin" else []
                self.assertEqual(json_search("apiKey", data, role=role), expected)

    def test_management_ip_permissions(self):
        """SR-02: Admins and operators can read management IPs; viewers cannot."""
        for role in ["admin", "operator", "viewer"]:
            with self.subTest(role=role):
                expected = [] if role == "viewer" else ["10.10.20.21"]
                self.assertEqual(
                    json_search("managementIpAddress", data, role=role), expected
                )

    def test_issue_summary_permissions(self):
        """SR-03: Each supported role can read the issue summary."""
        for role in ["admin", "operator", "viewer"]:
            with self.subTest(role=role):
                self.assertEqual(
                    json_search("issueSummary", data, role=role),
                    ["Network Device 10.10.20.82 Is Unreachable From Controller"],
                )

    def test_denies_missing_and_unknown_roles(self):
        """SR-04: Missing, unknown, and incorrectly cased roles have no protected access."""
        for key in POLICY:
            with self.subTest(key=key, role="omitted"):
                self.assertEqual(json_search(key, data), [])
            for role in [None, "", "guest", "Admin"]:
                with self.subTest(key=key, role=role):
                    self.assertEqual(json_search(key, data, role=role), [])

    def test_permissions_at_every_depth(self):
        """SR-05: Apply the policy to every match across mixed nesting levels."""
        for key, allowed_roles in POLICY.items():
            source = {
                key: "root",
                "children": [{key: "child"}, [[{"nested": {key: "deep"}}]]],
            }
            for role in ["admin", "operator", "viewer", "guest", None]:
                with self.subTest(key=key, role=role):
                    expected = ["root", "child", "deep"] if role in allowed_roles else []
                    self.assertEqual(json_search(key, source, role=role), expected)

    def test_parent_search_filters_protected_fields(self):
        """Returning a public parent cannot expose protected nested fields or mutate input."""
        source = {"device": {
            "name": "switch",
            "apiKey": "secret",
            "children": [{"managementIpAddress": "10.0.0.1", "status": "up"}],
        }}
        original = deepcopy(source)
        self.assertEqual(json_search("device", source, role="viewer"), [
            {"name": "switch", "children": [{"status": "up"}]}
        ])
        self.assertEqual(json_search("device", source, role="operator"), [
            {"name": "switch", "children": [
                {"managementIpAddress": "10.0.0.1", "status": "up"}
            ]}
        ])
        self.assertEqual(json_search("device", source, role="admin"), [original["device"]])
        self.assertEqual(source, original)

    def test_protected_subtree_cannot_be_searched_indirectly(self):
        """A public child key cannot bypass access control on its protected parent."""
        source = {"apiKey": {"value": "secret"}, "public": {"value": "visible"}}
        self.assertEqual(json_search("value", source, role="viewer"), ["visible"])
        self.assertEqual(json_search("value", source, role="admin"), ["secret", "visible"])

    def test_unprotected_fields_are_public(self):
        """Fields outside POLICY remain readable without a recognized role."""
        for role in [None, "guest", "viewer"]:
            with self.subTest(role=role):
                self.assertEqual(json_search("status", data, role=role), ["NEW"])


if __name__ == "__main__":
    unittest.main()
