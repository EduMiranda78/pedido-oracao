from pathlib import Path
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
import json
import os
import subprocess
import sys

from .models import PrayerRequest


class PrayerRequestTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="teste",
            password="senha-teste-123",
        )

    def test_health(self):
        response = self.client.get(
            reverse("health")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_create_prayer_request(self):
        self.client.login(
            username="teste",
            password="senha-teste-123",
        )

        response = self.client.post(
            reverse("prayer_create"),
            {
                "requester_name": "Maria",
                "requester_origin": "Rio de Janeiro/RJ",
                "beneficiary_name": "João",
                "prayer_text": "Pedido de teste",
                "status": PrayerRequest.Status.NEW,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            PrayerRequest.objects.count(),
            1,
        )

        prayer = PrayerRequest.objects.first()

        self.assertEqual(
            prayer.created_by,
            self.user,
        )
        self.assertEqual(
            prayer.requester_origin,
            "Rio de Janeiro/RJ",
        )


    def test_requester_origin_is_required_on_form(self):
        self.client.login(username="teste", password="senha-teste-123")
        response = self.client.post(
            reverse("prayer_create"),
            {
                "requester_name": "Maria",
                "requester_origin": "",
                "beneficiary_name": "João",
                "prayer_text": "Pedido de teste",
                "status": PrayerRequest.Status.NEW,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este campo é obrigatório")
        self.assertEqual(PrayerRequest.objects.count(), 0)

class LoginExperienceTests(TestCase):
    def test_login_has_contacts_without_install_button(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "data-install-app")
        self.assertNotContains(response, "login-install-top")
        self.assertNotContains(response, "data-install-hint")
        self.assertContains(response, "linkedin.com/in/eduardoomiranda")
        self.assertContains(response, "wa.me/351938823172")

    def test_service_worker_is_public(self):
        response = self.client.get(reverse("service_worker"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Service-Worker-Allowed"], "/")
        self.assertIn("application/javascript", response["Content-Type"])


class PWAInstallabilityTests(TestCase):
    def test_manifest_is_public_and_installable_shape(self):
        response = self.client.get(reverse("manifest"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/manifest+json", response["Content-Type"])
        body = b"".join(response.streaming_content)
        manifest = json.loads(body.decode("utf-8"))
        self.assertEqual(manifest["start_url"], "/login/?source=pwa")
        self.assertEqual(manifest["display"], "standalone")
        self.assertFalse(manifest["prefer_related_applications"])
        sizes = {icon["sizes"] for icon in manifest["icons"]}
        self.assertIn("192x192", sizes)
        self.assertIn("512x512", sizes)

    def test_offline_page_is_public(self):
        response = self.client.get(reverse("offline"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conexão indisponível")

    def test_service_worker_handles_navigation_and_scope(self):
        response = self.client.get(reverse("service_worker"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Service-Worker-Allowed"], "/")
        self.assertIn("no-cache", response["Cache-Control"])
        content = response.content.decode("utf-8")
        self.assertIn("event.request.mode === 'navigate'", content)
        self.assertIn("/offline/", content)

class PWAClientScriptTests(TestCase):
    def test_client_keeps_service_worker_without_install_button_logic(self):
        from django.contrib.staticfiles import finders
        path = finders.find("js/app.js")
        self.assertTrue(path)
        content = Path(path).read_text(encoding="utf-8")
        self.assertIn("navigator.serviceWorker.register('/sw.js'", content)
        self.assertNotIn("beforeinstallprompt", content)
        self.assertNotIn("data-install-app", content)



class SecuritySettingsTests(TestCase):
    def test_https_security_settings_are_configurable_by_environment(self):
        env = os.environ.copy()
        env.update({
            "DJANGO_SECRET_KEY": "test-only-secret",
            "POSTGRES_DB": "test_db",
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_password",
            "POSTGRES_HOST": "127.0.0.1",
            "POSTGRES_PORT": "5432",
            "DJANGO_SECURE_COOKIES": "True",
            "DJANGO_CSRF_TRUSTED_ORIGINS": (
                "https://app.example,https://app.example:9440"
            ),
        })
        code = (
            "import json; import config.settings as s; "
            "print(json.dumps({"
            "'csrf': s.CSRF_COOKIE_SECURE, "
            "'session': s.SESSION_COOKIE_SECURE, "
            "'origins': s.CSRF_TRUSTED_ORIGINS"
            "}))"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            env=env,
            cwd=Path(__file__).resolve().parent.parent,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(result.stdout.strip())
        self.assertTrue(payload["csrf"])
        self.assertTrue(payload["session"])
        self.assertEqual(
            payload["origins"],
            ["https://app.example", "https://app.example:9440"],
        )
