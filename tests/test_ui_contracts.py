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

    def test_mobile_viewport_and_meta(self):
        response = self.client.get("/")
        html = response.data.decode("utf-8")
        self.assertIn("viewport-fit=cover", html)
        self.assertIn("theme-color", html)
        self.assertIn("mobile-web-app-capable", html)

    def test_mobile_css_rules_present(self):
        response = self.client.get("/static/css/style.css")
        self.assertEqual(response.status_code, 200)
        css = response.data.decode("utf-8")
        self.assertIn("@media (max-width: 640px)", css)
        self.assertIn("@media (max-width: 380px)", css)
        self.assertIn("safe-area-inset", css)
        response.close()

if __name__ == "__main__":
    unittest.main()
