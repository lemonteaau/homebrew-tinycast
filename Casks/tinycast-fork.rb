cask "tinycast-fork" do
  version "0.12.1-fork.59"
  sha256 "af6993117592eed3a936b4c8c277d0ff04d2f7fc84664ca9dca7b7ceb6ef730d"

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
