import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("update_cask", ROOT / "Scripts/update-cask.py")
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
TEMPLATE = (ROOT / "Templates/tinycast-fork.rb").read_text()
SHA = "a" * 64


class ReleaseValidationTests(unittest.TestCase):
    def release(self):
        tag = "v0.11.3-fork.5"
        return {"tag_name": tag, "draft": False, "prerelease": False, "assets": [
            {"name": name, "browser_download_url":
             f"https://github.com/lemonteaau/tinycast/releases/download/{tag}/{name}"}
            for name in ("Tinycast-0.11.3-fork.5.dmg", "SHA256SUMS.txt")
        ]}

    def test_assets_require_published_release_and_exact_urls(self):
        self.assertEqual(publisher.release_assets(self.release())[0], "0.11.3-fork.5")
        for flag in ("draft", "prerelease"):
            release = self.release()
            release[flag] = True
            with self.assertRaises(ValueError):
                publisher.release_assets(release)
        release = self.release()
        release["assets"][0]["browser_download_url"] = "https://example.com/file.dmg"
        with self.assertRaises(ValueError):
            publisher.release_assets(release)
        release = self.release()
        release["assets"].append(release["assets"][0])
        with self.assertRaises(ValueError):
            publisher.release_assets(release)

    def test_manifest_must_match_actual_dmg(self):
        for prefix in ("", "./", "*"):
            publisher.verify_checksum(f"{SHA}  {prefix}app.dmg\n", "app.dmg", SHA)
        for manifest in (f"{'b' * 64}  app.dmg", f"{SHA}  other.dmg", "",
                         f"{SHA}  app.dmg\n{SHA}  app.dmg"):
            with self.assertRaises(ValueError):
                publisher.verify_checksum(manifest, "app.dmg", SHA)

    def test_revision_order_and_immutable_versions(self):
        current = publisher.render_cask(TEMPLATE, "", "0.11.3-fork.9", SHA)
        updated = publisher.render_cask(TEMPLATE, current, "0.11.3-fork.10", SHA)
        self.assertIn('version "0.11.3-fork.10"', updated)
        self.assertEqual(publisher.render_cask(TEMPLATE, updated, "0.11.3-fork.10", SHA), updated)
        with self.assertRaises(ValueError):
            publisher.render_cask(TEMPLATE, updated, "0.11.3-fork.9", SHA)
        with self.assertRaises(ValueError):
            publisher.render_cask(TEMPLATE, updated, "0.11.3-fork.10", "b" * 64)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.previous_directory = Path.cwd()
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.remote = self.root / "remote.git"
        publisher.run("git", "init", "--bare", "--initial-branch=main", str(self.remote))
        publisher.run("git", "clone", str(self.remote), str(self.root / "checkout"))
        os.chdir(self.root / "checkout")
        publisher.run("git", "config", "user.name", "Test")
        publisher.run("git", "config", "user.email", "test@example.com")
        Path("Templates").mkdir()
        Path("Casks").mkdir()
        publisher.TEMPLATE.write_text(TEMPLATE)
        publisher.CASK.write_text(publisher.render_cask(TEMPLATE, "", "0.11.3-fork.5", SHA))
        publisher.run("git", "add", ".")
        publisher.run("git", "commit", "-m", "initial")
        publisher.run("git", "push", "origin", "main")

    def tearDown(self):
        os.chdir(self.previous_directory)
        self.directory.cleanup()

    def test_publish_then_rerun_creates_only_one_commit(self):
        with patch.object(publisher, "verified_release", return_value=("0.11.3-fork.6", SHA)):
            self.assertIn("published and verified", publisher.publish())
            first = publisher.run("git", "rev-parse", "HEAD")
            self.assertIn("no changes needed", publisher.publish())
            self.assertEqual(publisher.run("git", "rev-parse", "HEAD"), first)

    def test_conflicting_push_fetches_latest_release_without_downgrading(self):
        original_run = publisher.run
        raced = False

        def concurrent_push(*args):
            nonlocal raced
            if args == ("git", "push", "origin", "HEAD:main") and not raced:
                raced = True
                rival = self.root / "rival"
                original_run("git", "clone", str(self.remote), str(rival))
                original_run("git", "-C", str(rival), "config", "user.name", "Rival")
                original_run("git", "-C", str(rival), "config", "user.email", "rival@example.com")
                (rival / publisher.CASK).write_text(
                    publisher.render_cask(TEMPLATE, "", "0.11.3-fork.7", SHA))
                original_run("git", "-C", str(rival), "add", ".")
                original_run("git", "-C", str(rival), "commit", "-m", "concurrent release")
                original_run("git", "-C", str(rival), "push", "origin", "main")
            return original_run(*args)

        with patch.object(publisher, "run", side_effect=concurrent_push), \
                patch.object(publisher, "verified_release", side_effect=[
                    ("0.11.3-fork.6", SHA), ("0.11.3-fork.7", SHA)]), \
                patch.object(publisher.time, "sleep"):
            self.assertIn("no changes needed", publisher.publish())
        self.assertTrue(raced)
        self.assertIn('version "0.11.3-fork.7"', publisher.CASK.read_text())

    def test_permission_failure_cannot_report_success(self):
        original_run = publisher.run

        def rejected_push(*args):
            if args == ("git", "push", "origin", "HEAD:main"):
                raise subprocess.CalledProcessError(1, args)
            return original_run(*args)

        with patch.object(publisher, "run", side_effect=rejected_push), \
                patch.object(publisher, "verified_release", return_value=("0.11.3-fork.6", SHA)), \
                patch.object(publisher.time, "sleep"), \
                self.assertRaises(subprocess.CalledProcessError):
            publisher.publish()
        remote = original_run("git", "show", "origin/main:Casks/tinycast-fork.rb")
        self.assertIn('version "0.11.3-fork.5"', remote)

    def test_dirty_checkout_is_rejected(self):
        publisher.CASK.write_text("local edits")
        with self.assertRaises(ValueError):
            publisher.publish()
        self.assertEqual(publisher.CASK.read_text(), "local edits")


if __name__ == "__main__":
    unittest.main()
