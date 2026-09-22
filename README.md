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
handle subsequent upgrades through its in-app updater. This tap's [daily Action](.github/workflows/update-cask.yml)
tracks the latest tested, signed fork release, so fresh Homebrew installs get the newest build.
Manual refresh: run that Action in this tap's Actions tab.

The cask supports macOS 26+ on Apple silicon. The fork currently does not publish an Intel build.
See the [fork maintenance notes](https://github.com/lemonteaau/tinycast/blob/main/docs/fork.md)
for upstream syncing, release signatures and first-install details.
