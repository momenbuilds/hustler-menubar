import json
import os
import shutil
import tempfile
import unittest
import zipfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import hustler


class HustlerProductFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_data_file = hustler.DATA_FILE
        self.original_backup_dir = hustler.BACKUP_DIR
        hustler.DATA_FILE = os.path.join(self.temp_dir.name, "hustler_data.json")
        hustler.BACKUP_DIR = os.path.join(self.temp_dir.name, "Backups")
        self.data = hustler.load_data()

    def tearDown(self):
        hustler.DATA_FILE = self.original_data_file
        hustler.BACKUP_DIR = self.original_backup_dir
        self.temp_dir.cleanup()

    def test_quick_log_parses_revenue_and_categorized_expense(self):
        self.assertEqual(hustler.parse_quick_log("+1,250 client work", self.data)[:3], ("revenue", 1250.0, "client work"))
        self.assertEqual(hustler.parse_quick_log("-20 Food lunch", self.data), ("expenses", 20.0, "lunch", "Food"))

    def test_backup_restore_preserves_current_data_before_replacing_it(self):
        self.data["revenue"].append({
            "amount": 400.0,
            "description": "first win",
            "timestamp": datetime.now().isoformat(),
            "goal_id": hustler.active_goal(self.data)["id"],
        })
        hustler.save_data(self.data)
        backup = hustler.create_backup()

        self.data["revenue"].append({
            "amount": 99.0,
            "description": "later win",
            "timestamp": datetime.now().isoformat(),
            "goal_id": hustler.active_goal(self.data)["id"],
        })
        hustler.save_data(self.data)
        restored = hustler.restore_backup(backup)

        self.assertEqual(hustler.revenue_total(restored), 400.0)
        self.assertGreaterEqual(len(os.listdir(hustler.BACKUP_DIR)), 2)

    def test_next_milestone_shows_the_nearest_reachable_win(self):
        goal = hustler.active_goal(self.data)
        goal["target"] = 1000.0
        self.data["revenue"].append({
            "amount": 180.0,
            "description": "progress",
            "timestamp": datetime.now().isoformat(),
            "goal_id": goal["id"],
        })
        next_win = hustler.next_milestone(self.data)
        self.assertEqual(next_win["label"], "25% milestone")
        self.assertEqual(next_win["remaining"], 70.0)

    def test_latest_release_chooses_the_matching_architecture_asset(self):
        response = {
            "tag_name": "v9.0.0",
            "body": "Improved backups.",
            "html_url": "https://example.com/release",
            "assets": [
                {"name": "Hustler-macOS-x86_64.zip", "browser_download_url": "https://example.com/intel"},
                {"name": "Hustler-macOS-arm64.zip", "browser_download_url": "https://example.com/arm"},
            ],
        }

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

        with patch.object(hustler, "urlopen", return_value=FakeResponse()), \
             patch.object(hustler.json, "load", return_value=response), \
             patch.object(hustler.platform, "machine", return_value="x86_64"):
            latest = hustler.latest_release()

        self.assertEqual(latest["url"], "https://example.com/intel")
        self.assertEqual(latest["notes"], "Improved backups.")

    def test_stage_update_unpacks_a_valid_hustler_app(self):
        archive_path = os.path.join(self.temp_dir.name, "update.zip")
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("Hustler.app/Contents/MacOS/Hustler", "executable")

        staged = hustler.stage_update(Path(archive_path).as_uri())

        self.assertTrue(os.path.isfile(os.path.join(staged, "Contents", "MacOS", "Hustler")))
        shutil.rmtree(os.path.dirname(staged), ignore_errors=True)

    def test_stage_update_rejects_unsafe_zip_paths(self):
        archive_path = os.path.join(self.temp_dir.name, "unsafe-update.zip")
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("../outside", "nope")

        with self.assertRaises(ValueError):
            hustler.stage_update(Path(archive_path).as_uri())

    def test_schedule_update_install_hands_off_to_a_helper(self):
        staged = os.path.join(self.temp_dir.name, "staged", "Hustler.app")
        target = os.path.join(self.temp_dir.name, "target", "Hustler.app")
        os.makedirs(staged)
        os.makedirs(target)

        with patch.object(hustler.subprocess, "Popen") as popen:
            hustler.schedule_update_install(staged, target)

        helper_path = os.path.join(os.path.dirname(staged), "install-update.sh")
        self.assertTrue(os.path.isfile(helper_path))
        popen.assert_called_once()


if __name__ == "__main__":
    unittest.main()
