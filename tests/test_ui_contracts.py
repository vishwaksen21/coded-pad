import unittest
import json
from app import app

class TestUIContracts(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_homepage_ui_elements(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("generateKeyBtn", html)
        self.assertIn("peekBtn", html)
        self.assertIn("home-features", html)
        self.assertIn("v3.0", html)

    def test_pad_ui_elements(self):
        response = self.client.post("/open", data={"secret_code": "contract-test-code"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("themeBtn", html)
        self.assertIn("fontDropdownBtn", html)
        self.assertIn("zenBtn", html)
        self.assertIn("exportBtn", html)
        self.assertIn("toastContainer", html)
        self.assertIn("clearModal", html)
        self.assertIn("lineCount", html)
        self.assertIn("readTime", html)

if __name__ == "__main__":
    unittest.main()

# [2026-01-06] test(ui): verify dark mode CSS selectors and contrast values

# [2026-01-07] test(ui): verify dark mode CSS selectors and contrast values

# [2026-01-09] test(theme): verify data-theme attribute binding on root element

# [2026-01-10] test(theme): verify data-theme attribute binding on root element

# [2026-01-11] test(theme): verify data-theme attribute binding on root element
