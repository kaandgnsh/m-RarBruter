import io
import tempfile
import types
import unittest
from pathlib import Path

from importlib.util import module_from_spec, spec_from_file_location


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "m-RarBruter"
    / "m-RarBruter.py"
)
SPEC = spec_from_file_location("rarbruter", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load m-RarBruter.")
rarbruter = module_from_spec(SPEC)
SPEC.loader.exec_module(rarbruter)


class ScanWordlistTests(unittest.TestCase):
    def test_finds_password_and_reports_count(self):
        with tempfile.TemporaryDirectory() as directory:
            wordlist = Path(directory) / "words.txt"
            wordlist.write_text("wrong\n\nsecret\nignored\n", encoding="utf-8")
            checked = []

            result = rarbruter.scan_wordlist(
                wordlist,
                4,
                lambda candidate: checked.append(candidate) is None and candidate == "secret",
            )

            self.assertEqual(result, ("secret", 2, 3))
            self.assertEqual(checked, ["wrong", "secret"])

    def test_enforces_line_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            wordlist = Path(directory) / "words.txt"
            wordlist.write_text("one\ntwo\nsecret\n", encoding="utf-8")
            checked = []
            result = rarbruter.scan_wordlist(
                wordlist,
                2,
                lambda candidate: checked.append(candidate) is None and candidate == "secret",
            )
            self.assertEqual(result, (None, 2, 2))
            self.assertEqual(checked, ["one", "two"])

    def test_invalid_attempt_limit_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            wordlist = Path(directory) / "words.txt"
            wordlist.write_text("secret\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                rarbruter.scan_wordlist(wordlist, 0, lambda _candidate: False)
            with self.assertRaises(ValueError):
                rarbruter.scan_wordlist(
                    wordlist,
                    rarbruter.MAX_ALLOWED_ATTEMPTS + 1,
                    lambda _candidate: False,
                )

    def test_progress_callback(self):
        with tempfile.TemporaryDirectory() as directory:
            wordlist = Path(directory) / "words.txt"
            wordlist.write_text("".join(f"p{i}\n" for i in range(105)), encoding="utf-8")
            progress = []
            rarbruter.scan_wordlist(
                wordlist, 105, lambda _candidate: False, progress=progress.append
            )
            self.assertEqual(progress, [100])


class FakeWrongPassword(Exception):
    pass


class FakeArchive:
    def __init__(self, _path):
        self.checked = []
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.closed = True

    def needs_password(self):
        return True

    def testrar(self, pwd=None):
        self.checked.append(pwd)
        if pwd != "secret":
            raise FakeWrongPassword()


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        base = Path(self.tempdir.name)
        self.archive_path = base / "archive.rar"
        self.wordlist_path = base / "passwords.txt"
        self.archive_path.write_bytes(b"fake archive")
        self.wordlist_path.write_text("wrong\nsecret\n", encoding="utf-8")
        self.output = io.StringIO()
        self.archive_instances = []

        def archive_factory(path):
            archive = FakeArchive(path)
            self.archive_instances.append(archive)
            return archive

        self.backend = types.SimpleNamespace(
            RarFile=archive_factory,
            RarWrongPassword=FakeWrongPassword,
            Error=Exception,
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def args(self, *extra):
        return [
            "--archive", str(self.archive_path),
            "--wordlist", str(self.wordlist_path),
            *extra,
        ]

    def test_default_is_dry_run(self):
        result = rarbruter.main(self.args(), output=self.output)
        self.assertEqual(result, 0)
        self.assertIn("Dry run only", self.output.getvalue())
        self.assertEqual(self.archive_instances, [])

    def test_declining_confirmation_skips_tests(self):
        result = rarbruter.main(
            self.args("--run"),
            input_fn=lambda _prompt: "n",
            output=self.output,
            rarfile_module=self.backend,
        )
        self.assertEqual(result, 0)
        self.assertEqual(self.archive_instances, [])

    def test_confirmed_run_finds_password(self):
        result = rarbruter.main(
            self.args("--run"),
            input_fn=lambda _prompt: "yes",
            output=self.output,
            rarfile_module=self.backend,
        )
        self.assertEqual(result, 0)
        self.assertIn("Password found: 'secret'", self.output.getvalue())
        self.assertEqual(self.archive_instances[0].checked, ["wrong", "secret"])
        self.assertTrue(self.archive_instances[0].closed)

    def test_no_password_protection_is_rejected(self):
        class PlainArchive(FakeArchive):
            def needs_password(self):
                return False

        self.backend.RarFile = PlainArchive
        result = rarbruter.main(
            self.args("--run", "--yes"),
            output=self.output,
            rarfile_module=self.backend,
        )
        self.assertEqual(result, 2)
        self.assertIn("does not appear to contain password-protected", self.output.getvalue())

    def test_yes_requires_run(self):
        with self.assertRaises(SystemExit) as raised:
            rarbruter.main(self.args("--yes"), output=self.output)
        self.assertEqual(raised.exception.code, 2)

    def test_attempt_limit_is_validated(self):
        with self.assertRaises(SystemExit) as raised:
            rarbruter.main(self.args("--max-attempts", "10001"), output=self.output)
        self.assertEqual(raised.exception.code, 2)

    def test_same_file_is_rejected(self):
        with self.assertRaises(SystemExit) as raised:
            rarbruter.main(
                ["--archive", str(self.archive_path), "--wordlist", str(self.archive_path)],
                output=self.output,
            )
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
