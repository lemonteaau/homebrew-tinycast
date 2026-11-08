cask "tinycast-fork" do
  version "0.12.11-fork.81"
  sha256 "d47d37933d4ec0c4b99b6698a63ae576c3307ed802496013372427200c769663"

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
