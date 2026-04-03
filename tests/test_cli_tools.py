import json
import importlib.util
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


class CliToolTests(unittest.TestCase):
    def load_skill_writer_module(self):
        spec = importlib.util.spec_from_file_location(
            "skill_writer_module",
            REPO_ROOT / "tools" / "skill_writer.py",
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [PYTHON, *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def test_create_uses_name_from_meta_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            meta_path = tmpdir / "meta.json"
            persona_path = tmpdir / "persona.md"
            base_dir = tmpdir / "exes"

            meta_path.write_text(
                json.dumps(
                    {
                        "name": "Alice",
                        "profile": {
                            "gender": "女",
                            "rel_stage": "分手",
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            persona_path.write_text("## Layer 0\n- 嘴硬心软\n", encoding="utf-8")

            result = self.run_cli(
                "tools/skill_writer.py",
                "--action",
                "create",
                "--meta",
                str(meta_path),
                "--persona",
                str(persona_path),
                "--base-dir",
                str(base_dir),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("触发词：/alice", result.stdout)
            self.assertTrue((base_dir / "alice" / "SKILL.md").exists())

    def test_update_and_rollback_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            base_dir = tmpdir / "exes"
            persona_path = tmpdir / "persona.md"
            patch_path = tmpdir / "patch.md"

            persona_path.write_text("## Layer 0\n- 外冷内热\n", encoding="utf-8")
            patch_path.write_text("## Layer 2\n- 常说晚点回\n", encoding="utf-8")

            create = self.run_cli(
                "tools/skill_writer.py",
                "--action",
                "create",
                "--name",
                "alice",
                "--persona",
                str(persona_path),
                "--base-dir",
                str(base_dir),
            )
            self.assertEqual(create.returncode, 0, create.stderr)

            update = self.run_cli(
                "tools/skill_writer.py",
                "--action",
                "update",
                "--slug",
                "alice",
                "--persona-patch",
                str(patch_path),
                "--base-dir",
                str(base_dir),
            )
            self.assertEqual(update.returncode, 0, update.stderr)

            list_versions = self.run_cli(
                "tools/version_manager.py",
                "--action",
                "list",
                "--slug",
                "alice",
                "--base-dir",
                str(base_dir),
            )
            self.assertEqual(list_versions.returncode, 0, list_versions.stderr)
            self.assertIn("v1", list_versions.stdout)

            rollback = self.run_cli(
                "tools/version_manager.py",
                "--action",
                "rollback",
                "--slug",
                "alice",
                "--version",
                "v1",
                "--base-dir",
                str(base_dir),
            )
            self.assertEqual(rollback.returncode, 0, rollback.stderr)

            persona_content = (base_dir / "alice" / "persona.md").read_text(encoding="utf-8")
            self.assertNotIn("常说晚点回", persona_content)

    def test_parse_text_export_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            export_path = tmpdir / "chat.txt"
            export_path.write_text(
                "\n".join(
                    [
                        "2024-01-01 10:00 Alice：早安",
                        "2024-01-01 10:01 我：早",
                        "2024-01-01 10:02 Alice：记得吃饭",
                    ]
                ),
                encoding="utf-8",
            )

            result = self.run_cli(
                "tools/wechat_parser.py",
                "--txt",
                str(export_path),
                "--target",
                "Alice",
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            json_start = result.stdout.find("[")
            self.assertNotEqual(json_start, -1, result.stdout)
            payload = json.loads(result.stdout[json_start:])
            self.assertEqual(len(payload), 3)
            self.assertEqual(payload[0]["sender"], "them")

    def test_slugify_normalizes_pypinyin_output_to_lowercase(self) -> None:
        fake_module = types.SimpleNamespace(lazy_pinyin=lambda value: ["Alice", "Li"])

        with mock.patch.dict(sys.modules, {"pypinyin": fake_module}):
            module = self.load_skill_writer_module()
            self.assertEqual(module.slugify("Alice Li"), "alice_li")


if __name__ == "__main__":
    unittest.main()
