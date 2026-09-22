cask "tinycast-fork" do
  version "0.11.3-fork.8"
  sha256 "db661986e471737cd202e0bc6f3349bed6542ea45d8caf2f7db1ed007f88f3d9"

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
