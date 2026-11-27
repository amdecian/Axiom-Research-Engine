"""Synthetic tests only; never load a real private repository or manifest."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from scripts import publication_gate as gate


class PublicationGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "source"
        self.repo.mkdir()
        self.run_git("init", "-q")
        self.run_git("config", "user.name", "Synthetic Test")
        self.run_git("config", "user.email", "synthetic@example.invalid")
        self.run_git("config", "core.autocrlf", "false")
        self.run_git("config", "commit.gpgsign", "false")
        self.run_git("remote", "add", "origin", "https://github.com/example/synthetic-source.git")
        self.dest = "docs/publications/synthetic.md"
        self.file = self.repo / "publication/candidates/PUB-000001" / self.dest
        self.file.parent.mkdir(parents=True)
        self.data = b"# Synthetic result\nNo scientific claim.\n"
        self.file.write_bytes(self.data)
        self.run_git("add", ".")
        self.run_git("commit", "-qm", "synthetic fixture")
        self.manifest = {
            "schema_version": "publication-1", "release_id": "PUB-000001",
            "source_repository": "example/synthetic-source",
            "source_commit": self.run_git("rev-parse", "HEAD").strip(),
            "target_repository": gate.TARGET, "public_base_commit": "1" * 40,
            "reviews": {x: True for x in gate.REVIEW_FIELDS},
            "files": [{"path": self.dest, "sha256": gate.sha(self.data),
                       "bytes": len(self.data), "classification": "approved_public"}]
        }
        self.manifest_path = self.root / "manifest.json"
        self.out = self.root / "staged"

    def run_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args],
                                       stderr=subprocess.STDOUT, timeout=20).decode()

    def write(self, manifest=None):
        raw = json.dumps(self.manifest if manifest is None else manifest).encode()
        self.manifest_path.write_bytes(raw)
        return gate.sha(raw)

    def reject(self, manifest):
        self.write(manifest)
        with self.assertRaises(ValueError):
            gate.load_manifest(self.manifest_path)

    def test_exact_export_and_no_private_metadata(self):
        digest = self.write()
        # An uncommitted modification must never be exported.
        self.file.write_bytes(b"unreviewed working tree")
        result = gate.stage(self.repo, self.manifest_path, digest, True, self.out)
        self.assertEqual(result, {"files": 1, "bytes": len(self.data), "uploaded": False})
        self.assertEqual((self.out / self.dest).read_bytes(), self.data)
        self.assertEqual([x.relative_to(self.out).as_posix() for x in self.out.rglob("*") if x.is_file()], [self.dest])

    def test_no_implicit_approval(self):
        digest = self.write()
        for approval, confirm in ((digest, False), ("0"*64, True), (None, True)):
            with self.assertRaises(ValueError):
                gate.stage(self.repo, self.manifest_path, approval, confirm, self.out)
        self.assertFalse(self.out.exists())

    def test_changed_manifest(self):
        digest = self.write()
        self.manifest_path.write_bytes(self.manifest_path.read_bytes() + b"\n")
        with self.assertRaises(ValueError):
            gate.stage(self.repo, self.manifest_path, digest, True, self.out)

    def test_wrong_target_source_and_revision(self):
        for key, value in (("target_repository", "example/other"), ("source_repository", gate.TARGET),
                           ("source_commit", "main"), ("public_base_commit", "HEAD"), ("release_id", "../x")):
            self.reject(self.manifest | {key: value})
        for key, value in (("source_repository", "example/other"), ("source_commit", "0"*40)):
            digest = self.write(self.manifest | {key: value})
            with self.assertRaises(ValueError):
                gate.stage(self.repo, self.manifest_path, digest, True, self.out)

    def test_all_reviews_required(self):
        for field in gate.REVIEW_FIELDS:
            self.reject(self.manifest | {"reviews": self.manifest["reviews"] | {field: False}})
        self.reject(self.manifest | {"reviews": self.manifest["reviews"] | {"owner": 1}})

    def test_unknown_duplicate_and_oversize_manifest(self):
        self.reject(self.manifest | {"extra": True})
        self.manifest_path.write_text('{"schema_version":"publication-1","schema_version":"publication-1"}')
        with self.assertRaises(ValueError):
            gate.load_manifest(self.manifest_path)
        self.manifest_path.write_bytes(b"x" * (gate.MAX_MANIFEST + 1))
        with self.assertRaises(ValueError):
            gate.load_manifest(self.manifest_path)

    def test_forbidden_paths(self):
        for path in ("../a.md", "/docs/publications/a.md", "docs/publications/../a.md",
                     "docs/publications/.git/config", "docs/publications/CON.txt", "docs/publications/a.",
                     "docs/publications/AUX.md", "docs/publications/a.md:stream",
                     "docs\\publications\\a.md", "docs/publications/a.zip", "docs/publications/a.exe",
                     ".github/workflows/x.yml", "research/notebook/L000001.json", "verification/holdouts/x.json",
                     "docs/publications/%2e%2e/x.md", "docs/publications//a.md"):
            with self.subTest(path=path):
                self.reject(self.manifest | {"files": [self.manifest["files"][0] | {"path": path}]})

    def test_case_duplicates_and_collisions(self):
        entry = self.manifest["files"][0]
        for other in (entry, entry | {"path": "docs/publications/SYNTHETIC.md"},
                      entry | {"path": self.dest + "/a.md"}):
            self.reject(self.manifest | {"files": [entry, other]})
        self.reject(self.manifest | {"files": [entry | {"path": "docs/publications/A/x.md"},
                                                 entry | {"path": "docs/publications/a/y.md"}]})

    def test_reject_classification_invalid_size_and_hash(self):
        entry = self.manifest["files"][0]
        for key, value in (("classification", "private"), ("bytes", True), ("bytes", 0),
                           ("bytes", gate.MAX_FILE+1), ("sha256", "0"*63)):
            self.reject(self.manifest | {"files": [entry | {key: value}]})
        for key, value in (("bytes", len(self.data)+1), ("sha256", "0"*64)):
            digest = self.write(self.manifest | {"files": [entry | {key: value}]})
            with self.assertRaises(ValueError):
                gate.stage(self.repo, self.manifest_path, digest, True, self.out)

    def test_file_and_total_limit(self):
        entry = self.manifest["files"][0]
        self.reject(self.manifest | {"files": [entry | {"path": f"docs/publications/a{i}.md"} for i in range(33)]})
        self.reject(self.manifest | {"files": [entry | {"path": f"docs/publications/a{i}.md", "bytes": gate.MAX_FILE} for i in range(5)]})

    def commit_bytes(self, value, executable=False):
        self.file.write_bytes(value)
        self.run_git("add", str(self.file))
        if executable:
            self.run_git("update-index", "--chmod=+x", self.file.relative_to(self.repo).as_posix())
        self.run_git("commit", "-qm", "synthetic mutation")
        self.manifest["source_commit"] = self.run_git("rev-parse", "HEAD").strip()
        self.manifest["files"][0].update(bytes=len(value), sha256=gate.sha(value))
        return self.write()

    def test_sensitive_and_binary_controls(self):
        samples = [b"PRIVATE_" + b"ONLY\n", b"-----BEGIN " + b"PRIVATE KEY-----\n",
                   b"ghp_" + b"A"*32, b"password" + b"=synthetic123456",
                   b"Bearer " + b"abcdefghijk123456789", b"hello\x00world", b"\xff",
                   b"bad\r\n", "bad\u202e".encode(), b"version https://git-lfs.github.com/spec/v1\n", b"example/synthetic-source\n"]
        for value in samples:
            with self.subTest(length=len(value)):
                digest = self.commit_bytes(value)
                with self.assertRaises(ValueError):
                    gate.stage(self.repo, self.manifest_path, digest, True, self.out)
                self.assertFalse(self.out.exists())

    def test_executable_and_symlink_git_modes(self):
        digest = self.commit_bytes(b"synthetic changed text\n", executable=True)
        with self.assertRaises(ValueError):
            gate.stage(self.repo, self.manifest_path, digest, True, self.out)
        # Create a symlink Git blob without depending on Windows symlink privileges.
        blob = self.run_git("rev-parse", "HEAD:" + self.file.relative_to(self.repo).as_posix()).strip()
        self.run_git("update-index", "--cacheinfo", "120000," + blob + "," + self.file.relative_to(self.repo).as_posix())
        self.run_git("commit", "-qm", "synthetic link")
        self.manifest["source_commit"] = self.run_git("rev-parse", "HEAD").strip()
        with self.assertRaises(ValueError):
            gate.stage(self.repo, self.manifest_path, self.write(), True, self.out)

    def test_missing_candidate_and_existing_or_checkout_destination(self):
        digest = self.write()
        self.out.mkdir()
        with self.assertRaises(ValueError):
            gate.stage(self.repo, self.manifest_path, digest, True, self.out)
        with self.assertRaises(ValueError):
            gate.stage(self.repo, self.manifest_path, digest, True, self.repo / "out")
        self.manifest["files"][0]["path"] = "docs/publications/missing.md"
        with self.assertRaises(ValueError):
            gate.stage(self.repo, self.manifest_path, self.write(), True, self.root / "new")


if __name__ == "__main__":
    unittest.main()
