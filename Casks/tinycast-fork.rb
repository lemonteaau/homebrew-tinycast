cask "tinycast-fork" do
  version "0.11.19-fork.48"
  sha256 "6ef8df7e03fe2035ae5dec423e61a12c1632153e18f88b6da7fc7668d0cf59e2"

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
