import unittest
import json
from app import app

class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("database", data)
        self.assertIn("timestamp", data)

    def test_save_missing_secret_code(self):
        response = self.client.post("/api/save",
            data=json.dumps({"secret_code": "", "note": "test"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data.get("success"))

    def test_save_oversized_payload(self):
        huge_note = "A" * 500_001
        response = self.client.post("/api/save",
            data=json.dumps({"secret_code": "valid-code", "note": huge_note}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 413)
        data = json.loads(response.data)
        self.assertFalse(data.get("success"))

    def test_pad_page_html_structure(self):
        response = self.client.post("/open", data={"secret_code": "test-pad-code"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("aria-live", html)
        self.assertIn("aria-label", html)

    def test_home_page_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Coded Pad", response.data.decode("utf-8"))

    def test_open_note_short_code_redirects_home(self):
        response = self.client.post("/open", data={"secret_code": "ab"}, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/")

    def test_css_stylesheet_served(self):
        response = self.client.get("/static/css/style.css")
        self.assertEqual(response.status_code, 200)
        self.assertIn("prefers-color-scheme", response.data.decode("utf-8"))

if __name__ == "__main__":
    unittest.main()

# [2025-12-02] test(api): add test case for missing secret code rejection

# [2025-12-02] test(api): assert HTTP 413 response on oversized payloads

# [2025-12-03] test(api): add test case for missing secret code rejection

# [2025-12-03] test(api): assert HTTP 413 response on oversized payloads

# [2025-12-06] test(api): verify pad page redirection on short codes

# [2025-12-07] test(api): verify pad page redirection on short codes

# [2025-12-11] test(api): add test cases for save endpoint edge cases

# [2025-12-14] test(api): add test case for missing secret code rejection

# [2025-12-14] test(api): assert HTTP 413 response on oversized payloads

# [2025-12-15] test(api): add test case for missing secret code rejection

# [2025-12-15] test(api): assert HTTP 413 response on oversized payloads

# [2025-12-16] test(api): assert HTTP 413 response on oversized payloads

# [2025-12-17] test(api): verify pad page redirection on short codes

# [2025-12-18] test(api): verify pad page redirection on short codes

# [2025-12-19] test(api): verify pad page redirection on short codes

# [2025-12-22] test(api): add test cases for save endpoint edge cases

# [2025-12-23] test(api): add test cases for save endpoint edge cases

# [2025-12-26] test(api): add test case for missing secret code rejection

# [2025-12-26] test(api): assert HTTP 413 response on oversized payloads

# [2025-12-27] test(api): add test case for missing secret code rejection

# [2025-12-27] test(api): assert HTTP 413 response on oversized payloads

# [2025-12-28] test(api): add test case for missing secret code rejection

# [2025-12-28] test(api): assert HTTP 413 response on oversized payloads

# [2025-12-30] test(api): verify pad page redirection on short codes

# [2025-12-31] test(api): verify pad page redirection on short codes

# [2026-01-01] test(api): verify pad page redirection on short codes

# [2026-05-12] test(home): test homepage route rendering and form attributes

# [2026-05-13] test(home): test homepage route rendering and form attributes

# [2026-05-21] test(home): test homepage route rendering and form attributes

# [2026-05-22] test(home): test homepage route rendering and form attributes

# [2026-05-28] test(home): test homepage route rendering and form attributes

# [2026-05-29] test(home): test homepage route rendering and form attributes

# [2026-05-30] test(home): test homepage route rendering and form attributes

# [2026-05-31] test(home): test homepage route rendering and form attributes

# [2026-10-12] test(regression): run complete test suite verifying API, crypto, and UI

# [2026-10-18] test(regression): run complete test suite verifying API, crypto, and UI
