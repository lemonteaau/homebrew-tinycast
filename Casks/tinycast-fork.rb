cask "tinycast-fork" do
  version "0.11.3-fork.9"
  sha256 "e36bf752fb93c25f7e54f6eb4024cd6d96aefb568ae510442db66b6622e4daa0"

  url "https://github.com/lemonteaau/tinycast/releases/download/v#{version}/Tinycast-#{version}.dmg"
  name "Tinycast (lemonteaau fork)"
  desc "Native launcher with currency shorthand and automatic upstream sync"
  homepage "https://github.com/lemonteaau/tinycast"

  conflicts_with cask: [
    "abue-ammar/tinycast/tinycast",
    "abue-ammar/tinycast/tinycast-universal",
    "abue-ammar/tinycast/tinycast-sequoia",
  ]
  depends_on macos: :tahoe
  depends_on arch: :arm64
  auto_updates true

  app "Tinycast.app"

  postflight_steps do
    run "/usr/bin/xattr", args: ["-dr", "com.apple.quarantine", "{{appdir}}/Tinycast.app"]
  end

  uninstall quit: "com.tinycast.app"
end
