"""Offline exact-file export; never uploads, executes candidate code, or creates Git commits.

Use only a reviewed local source checkout and owner-authorized manifest. This
is a disclosure guard, not DLP, authentication, or a hostile-code sandbox.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys

TARGET = "amdecian/Axiom-Research-Engine"
MAX_MANIFEST = 64 * 1024
MAX_FILE = 256 * 1024
MAX_TOTAL = 1024 * 1024
MAX_FILES = 32
SHA256 = re.compile(r"[0-9a-f]{64}")
SHA1 = re.compile(r"[0-9a-f]{40}")
REPO = re.compile(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+")
SEGMENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}")
RESERVED = re.compile(r"(?:CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])(?:\..*)?", re.I)
PREFIXES = {
    "docs/publications/": {".md", ".txt", ".tex"},
    "research/published/": {".json", ".md", ".txt"},
    "evidence/publications/": {".json", ".txt", ".md", ".csv"},
    "axiom/": {".py"},
    "tests/": {".py"},
}
# Heuristics only. Never log matched bytes or file contents.
MARKERS = (
    re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----", re.I),
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|ASIA[A-Z0-9]{16}|sk-[A-Za-z0-9_-]{20,})\b"),
    re.compile(r"\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|client[_-]?secret)\s*[:=]\s*['\"]?[^\s'\"]{8,}", re.I),
    re.compile(r"\b(?:authorization\s*:\s*)?bearer\s+[A-Za-z0-9._~+/-]{16,}", re.I),
    re.compile(r"\b(?:PRIVATE_ONLY|CONFIDENTIAL|PRIVATE_RESEARCH|private-holdouts|publication/candidates|private[-_ ]lab)\b", re.I),
    re.compile(r"\bversion https://git-lfs.github.com/spec/v1\b"),
)
FIELDS = {"schema_version", "release_id", "source_repository", "source_commit",
          "target_repository", "public_base_commit", "reviews", "files"}
REVIEW_FIELDS = {"rights", "scientific", "security", "owner"}
ENTRY_FIELDS = {"path", "sha256", "bytes", "classification"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def validate_path(path):
    require(isinstance(path, str) and 0 < len(path) <= 220, "invalid path")
    parts = path.split("/")
    require(all(SEGMENT.fullmatch(x) and not x.endswith(".") and not RESERVED.fullmatch(x)
                for x in parts), "unsafe path segment")
    require(any(path.startswith(prefix) and PurePosixPath(path).suffix in suffixes
                for prefix, suffixes in PREFIXES.items()), "destination outside allowlist")
    return parts


def load_manifest(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "manifest must be a regular file")
    with path.open("rb") as f:
        raw = f.read(MAX_MANIFEST + 1)
    require(0 < len(raw) <= MAX_MANIFEST, "manifest size")
    manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    require(isinstance(manifest, dict) and set(manifest) == FIELDS, "manifest fields")
    require(manifest["schema_version"] == "publication-1", "manifest version")
    rid = manifest["release_id"]
    require(isinstance(rid, str) and re.fullmatch(r"PUB-[0-9]{6}", rid), "release id")
    source = manifest["source_repository"]
    require(isinstance(source, str) and REPO.fullmatch(source) and source.casefold() != TARGET.casefold(), "source scope")
    require(manifest["target_repository"] == TARGET, "wrong public target")
    for field in ("source_commit", "public_base_commit"):
        value = manifest[field]
        require(isinstance(value, str) and SHA1.fullmatch(value), "full commit hash required")
    reviews = manifest["reviews"]
    require(isinstance(reviews, dict) and set(reviews) == REVIEW_FIELDS and
            all(value is True for value in reviews.values()), "all review attestations required")
    files = manifest["files"]
    require(isinstance(files, list) and 0 < len(files) <= MAX_FILES, "file count")
    seen = set()
    spelling = {}
    total = 0
    for item in files:
        require(isinstance(item, dict) and set(item) == ENTRY_FIELDS, "entry fields")
        parts = validate_path(item["path"])
        key = item["path"].casefold()
        require(key not in seen, "duplicate or case-colliding file")
        seen.add(key)
        for i in range(1, len(parts) + 1):
            p = "/".join(parts[:i])
            require(spelling.setdefault(p.casefold(), p) == p, "case-colliding directory")
        require(item["classification"] == "approved_public", "classification not approved")
        require(isinstance(item["sha256"], str) and SHA256.fullmatch(item["sha256"]), "invalid file hash")
        require(type(item["bytes"]) is int and 0 < item["bytes"] <= MAX_FILE, "file size")
        total += item["bytes"]
    require(not any("/".join(key.split("/")[:i]) in seen
                    for key in seen for i in range(1, len(key.split("/")))), "file/directory collision")
    require(total <= MAX_TOTAL, "total export size")
    return manifest, sha(raw)


def git(root, *args):
    # No filters, hooks, checkout, remote access or credential helpers.
    # Read a reviewed repository's local objects only. Do not fetch missing objects.
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1",
               GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0", GIT_ALLOW_PROTOCOL="")
    p = subprocess.run(["git", "-C", str(root), "--no-pager", "--literal-pathspecs", *args],
                       env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                       timeout=15, check=False)
    require(p.returncode == 0, "local Git object or configuration unavailable")
    return p.stdout


def source_identity(root, manifest):
    root = Path(root).resolve(strict=True)
    top = Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel").rstrip(b"\r\n"))).resolve(strict=True)
    require(root == top, "source must be repository root")
    origin = git(root, "config", "--local", "--get", "remote.origin.url").decode("utf-8").strip()
    name = manifest["source_repository"]
    allowed = {"https://github.com/" + name, "https://github.com/" + name + ".git",
               "git@github.com:" + name + ".git", "ssh://git@github.com/" + name + ".git"}
    require(origin in allowed, "source origin mismatch")
    # Local origin text is not proof of GitHub ownership or visibility.
    require(git(root, "rev-parse", "--verify", manifest["source_commit"] + "^{commit}").decode().strip() ==
            manifest["source_commit"], "source commit mismatch")
    return root


def read_candidate(root, manifest, entry):
    # Only deliberately prepared candidate files, not arbitrary research paths.
    path = "publication/candidates/" + manifest["release_id"] + "/" + entry["path"]
    listing = git(root, "ls-tree", "-z", manifest["source_commit"], "--", path)
    records = listing.split(b"\0")
    require(len(records) == 2 and records[-1] == b"", "missing or ambiguous candidate")
    meta, sep, actual_path = records[0].partition(b"\t")
    parts = meta.split()
    require(sep == b"\t" and actual_path == path.encode("ascii") and len(parts) == 3 and
            parts[0] == b"100644" and parts[1] == b"blob", "candidate is not a regular nonexecutable file")
    blob = parts[2].decode("ascii")
    require(SHA1.fullmatch(blob), "invalid object hash")
    require(int(git(root, "cat-file", "-s", blob)) == entry["bytes"], "candidate size changed")
    data = git(root, "cat-file", "blob", blob)
    require(len(data) == entry["bytes"] and sha(data) == entry["sha256"], "candidate hash changed")
    s = data.decode("utf-8", errors="strict")
    require(not any(ord(c) < 32 and c not in "\n\t" for c in s) and
            not any(ord(c) in (127, 0xfeff) or 0x202a <= ord(c) <= 0x202e or
                    0x2066 <= ord(c) <= 0x2069 for c in s), "noncanonical text or hidden controls")
    require(not any(pattern.search(s) for pattern in MARKERS), "potential sensitive marker; manual review required")
    folded = s.casefold()
    require(manifest["source_repository"].casefold() not in folded and
            manifest["source_repository"].split("/")[-1].casefold() not in folded and
            manifest["source_commit"] not in folded, "private source identity marker")
    return data


def verify(root, manifest):
    root = source_identity(root, manifest)
    return {entry["path"]: read_candidate(root, manifest, entry) for entry in manifest["files"]}


def stage(root, manifest_path, approval, confirm, destination):
    manifest, digest = load_manifest(manifest_path)
    require(confirm is True and isinstance(approval, str) and approval == digest,
            "explicit owner approval of exact manifest digest required")
    data = verify(root, manifest)
    out = Path(destination)
    require(not out.exists() and not out.is_symlink(), "destination already exists")
    out = out.resolve()
    require(out.parent.is_dir(), "existing destination parent required")
    require(not out.is_relative_to(Path(root).resolve()) and
            not any((parent / ".git").exists() or (parent / ".git").is_symlink()
                    for parent in (out.parent, *out.parent.parents)), "destination must be outside any checkout")
    out.mkdir(exist_ok=False, mode=0o700)
    try:
        for path, value in data.items():
            dest = out.joinpath(*path.split("/"))
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("xb") as f:
                f.write(value)
            require(sha(dest.read_bytes()) == sha(value), "staged hash mismatch")
    except BaseException:
        # Remove only this invocation's newly created staging directory.
        shutil.rmtree(out)
        raise
    return {"files": len(data), "bytes": sum(map(len, data.values())), "uploaded": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("preview", "stage"))
    p.add_argument("--source", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--out")
    p.add_argument("--approve-sha256")
    p.add_argument("--confirm-owner-approval", action="store_true")
    a = p.parse_args()
    try:
        if a.mode == "preview":
            require(a.out is None and a.approve_sha256 is None and not a.confirm_owner_approval, "preview has no write or approval options")
            m, digest = load_manifest(a.manifest)
            files = verify(a.source, m)
            print(json.dumps({"manifest_sha256": digest, "files": len(files), "bytes": sum(map(len, files.values())), "uploaded": False}))
        else:
            require(a.out is not None, "new staging directory required")
            print(json.dumps(stage(a.source, a.manifest, a.approve_sha256, a.confirm_owner_approval, a.out)))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as e:
        # Exception text from parsers/OS may contain private paths or source data.
        print("Publication gate stopped; inspect reviewed local inputs privately. " + type(e).__name__, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
