# Homebrew tap for lemonteaau's Tinycast fork

This tap installs [lemonteaau/tinycast](https://github.com/lemonteaau/tinycast), a personal fork
with currency shorthand such as `610 aud cny`. It follows the official Tinycast version and adds a
fork build revision, for example `0.11.3-fork.2`.

```sh
brew trust --cask lemonteaau/tinycast/tinycast-fork
brew install --cask lemonteaau/tinycast/tinycast-fork
```

The first install replaces an existing `Tinycast.app` with the same bundle identifier and keeps
its preferences and data. Quit Tinycast and back up the current app before switching signing
identities. You may need to grant Accessibility permission again after the replacement.
If the upstream cask is installed through Homebrew, uninstall that cask first without `--zap`;
do not delete its settings. Only one cask can own `/Applications/Tinycast.app` at a time.

The cask clears Gatekeeper quarantine after installation. Its `auto_updates true` lets Tinycast
handle subsequent upgrades through its in-app updater. The fork's release workflow calls this tap's
[reusable workflow](.github/workflows/update-cask.yml) immediately after publishing. The entire release
workflow succeeds only when the cask is verified remotely. The daily schedule at 21:31 UTC is a repair
path, not the normal publication path; **Run workflow** is also available without rebuilding the app.

The release job receives a dedicated SSH deploy key with write access to this tap only. Its private
key is stored as `HOMEBREW_TAP_DEPLOY_KEY` in `lemonteaau/tinycast` and passed only to the cask job.
No personal access token is stored. The daily/manual job uses this tap's own `GITHUB_TOKEN`.
The updater downloads the DMG, compares its SHA-256 with the release's checksum manifest, and then
commits the cask. Repeated runs are idempotent. Concurrent pushes retry against the current remote and
latest release; older releases cannot roll the cask back. A changed checksum for an existing version
fails instead of silently replacing it. Permission or verification failures fail the workflow.

After a successful release, explicitly refresh local metadata before upgrading:

```sh
brew update
brew upgrade --cask tinycast-fork
```

Plain `brew upgrade` may skip apps declaring `auto_updates true`; the named cask command above is
the supported Homebrew update path. CI updates the catalog; it does not install apps on your Mac.

Validate changes with `python3 -m unittest discover -s Tests -v` and `actionlint`.
`Scripts/update-cask.py` is intended for a disposable CI checkout: it refreshes `origin/main` on each
push attempt and refuses tracked local edits or unpublished local commits before starting.

The cask supports macOS 26+ on Apple silicon. The fork currently does not publish an Intel build.
See the [fork maintenance notes](https://github.com/lemonteaau/tinycast/blob/main/docs/fork.md)
for upstream syncing, release signatures and first-install details.
