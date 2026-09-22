#!/usr/bin/env python3
"""Publish the latest verified release from a disposable CI checkout."""

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time


REPOSITORY = "lemonteaau/tinycast"
CASK = Path("Casks/tinycast-fork.rb")
TEMPLATE = Path("Templates/tinycast-fork.rb")


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def version_key(version):
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)-fork\.(\d+)", version)
    if not match:
        raise ValueError(f"Unexpected fork version: {version}")
    return tuple(map(int, match.groups()))


def release_assets(release):
    tag = release["tag_name"]
    if release.get("draft") or release.get("prerelease") or not tag.startswith("v"):
        raise ValueError("Expected a published stable fork release")
    version = tag[1:]
    version_key(version)
    urls = {}
    for name in (f"Tinycast-{version}.dmg", "SHA256SUMS.txt"):
        assets = [asset for asset in release["assets"] if asset["name"] == name]
        expected = f"https://github.com/{REPOSITORY}/releases/download/{tag}/{name}"
        if len(assets) != 1 or assets[0]["browser_download_url"] != expected:
            raise ValueError(f"Missing or unexpected release asset: {name}")
        urls[name] = expected
    return version, urls


def verify_checksum(manifest, filename, digest):
    matches = []
    for line in manifest.splitlines():
        fields = line.split(maxsplit=1)
        if len(fields) != 2:
            continue
        name = fields[1].removeprefix("*").removeprefix("./")
        if name == filename:
            matches.append(fields[0])
    if len(matches) != 1 or matches[0] != digest:
        raise ValueError("Downloaded DMG does not match the published SHA256SUMS.txt")


def render_cask(template, current, version, digest):
    version_key(version)
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("Invalid SHA-256")
    if current:
        old_version = re.search(r'^  version "([^"]+)"$', current, re.MULTILINE)
        if not old_version:
            raise ValueError("Cannot determine the existing cask version")
        if version_key(old_version[1]) > version_key(version):
            raise ValueError("Refusing to downgrade the cask to an older release")
        old_sha = re.search(r'^  sha256 "([^"]+)"$', current, re.MULTILINE)
        if old_version[1] == version and (not old_sha or old_sha[1] != digest):
            raise ValueError("A published version's DMG checksum changed")
    if template.count("__VERSION__") != 1 or template.count("__SHA256__") != 1:
        raise ValueError("Cask template must have exactly one version and checksum placeholder")
    return template.replace("__VERSION__", version).replace("__SHA256__", digest)


def verified_release():
    release = json.loads(run("gh", "api", f"repos/{REPOSITORY}/releases/latest"))
    version, urls = release_assets(release)
    dmg = f"Tinycast-{version}.dmg"
    with tempfile.TemporaryDirectory(prefix="tinycast-cask-") as directory:
        for name, url in urls.items():
            run("curl", "--fail", "--silent", "--show-error", "--location",
                "--retry", "3", "--retry-all-errors", "--connect-timeout", "20",
                "--max-time", "120", url, "--output", str(Path(directory) / name))
        digest = hashlib.sha256((Path(directory) / dmg).read_bytes()).hexdigest()
        verify_checksum((Path(directory) / "SHA256SUMS.txt").read_text(), dmg, digest)
    return version, digest


def publish():
    if run("git", "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Refusing to publish from a checkout with tracked local changes")
    if run("git", "rev-parse", "HEAD") != run("git", "rev-parse", "origin/main"):
        raise ValueError("Expected a disposable checkout of origin/main")
    run("git", "config", "user.name", "github-actions[bot]")
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    for attempt in range(3):
        run("git", "fetch", "origin", "main")
        run("git", "reset", "--hard", "origin/main")
        version, digest = verified_release()
        current = CASK.read_text() if CASK.exists() else ""
        rendered = render_cask(TEMPLATE.read_text(), current, version, digest)
        if rendered == current:
            return f"Homebrew verified at {version} (SHA-256: {digest}); no changes needed."
        CASK.parent.mkdir(exist_ok=True)
        CASK.write_text(rendered)
        run("git", "add", str(CASK))
        run("git", "commit", "-m", f"Tinycast fork {version}")
        try:
            run("git", "push", "origin", "HEAD:main")
        except subprocess.CalledProcessError:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
            continue
        run("git", "fetch", "origin", "main")
        published = run("git", "show", f"origin/main:{CASK}")
        published_version = re.search(r'^  version "([^"]+)"$', published, re.MULTILINE)
        if not published_version or version_key(published_version[1]) < version_key(version):
            raise ValueError("Remote cask verification failed after push")
        if published_version[1] == version and f'  sha256 "{digest}"' not in published:
            raise ValueError("Remote cask checksum verification failed after push")
        return f"Homebrew published and verified at {version} (SHA-256: {digest})."
    raise RuntimeError("Homebrew publication exhausted retries")


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent.parent)
    summary = publish()
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as output:
            output.write(summary + "\n")
