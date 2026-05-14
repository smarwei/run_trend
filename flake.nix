{
  description = "Running Progress Tracker - Desktop application for tracking running progress from Strava";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          pyside6
          requests
          numpy
          markdown
          pytest
          pytest-cov
        ]);
      in
      {
        packages.default =
          let
            src = ./.;
            desktopFile = pkgs.runCommand "run-trend-desktop" { } ''
              mkdir -p $out/share/applications
              cp ${src}/de.arneweiss.RunTrend.desktop $out/share/applications/
            '';
          in
          pkgs.writeShellApplication {
            name = "run-trend";
            runtimeInputs = [ pythonEnv ];
            text = ''
              # Make the .desktop file visible to xdg-desktop-portal so it can
              # identify this app. GIO_LAUNCHED_DESKTOP_FILE is read by Qt before
              # QApplication is constructed (before setDesktopFileName() can be called).
              export XDG_DATA_DIRS="${desktopFile}/share:''${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
              export GIO_LAUNCHED_DESKTOP_FILE="${desktopFile}/share/applications/de.arneweiss.RunTrend.desktop"
              export GIO_LAUNCHED_DESKTOP_FILE_PID=$$
              cd ${src}
              exec python -m run_trend.main "$@"
            '';
          };

        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/run-trend";
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.qt6.qtbase
            pkgs.qt6.qtwayland
            pkgs.sqlite
            # Flatpak toolchain so `flatpak-builder` works out of the box
            # in the devshell. appstream brings the `appstreamcli` binary
            # that flatpak-builder shells out to during metainfo
            # compose — without it the build aborts before the export
            # step (no app gets installed). flatpak itself provides the
            # `flatpak` CLI used to install + run the resulting bundle.
            pkgs.flatpak
            pkgs.flatpak-builder
            pkgs.appstream
          ];

          shellHook = ''
            echo "Running Progress Tracker Development Environment"
            echo "Python: ${pythonEnv}/bin/python --version"
            echo ""
            echo "Available commands:"
            echo "  python -m run_trend.main          - Run the application"
            echo "  pytest tests/                     - Run tests"
            echo "  flatpak-builder --user --install \\"
            echo "    --force-clean --ccache \\"
            echo "    build-dir de.arneweiss.RunTrend.json  - Build + install Flatpak"
            echo "  flatpak run de.arneweiss.RunTrend - Run the installed Flatpak"
            echo ""
          '';

          QT_QPA_PLATFORM = "xcb";
          QT_PLUGIN_PATH = "${pkgs.qt6.qtbase}/${pkgs.qt6.qtbase.qtPluginPrefix}";
        };

        checks = {
          test = pkgs.stdenv.mkDerivation {
            pname = "run-trend-tests";
            version = "1.0.0";
            src = ./.;
            buildInputs = [ pythonEnv ];

            buildPhase = ''
              export HOME=$TMPDIR
              pytest tests/ -v
            '';

            installPhase = ''
              mkdir -p $out
              echo "Tests passed" > $out/result
            '';
          };
        };
      }
    );
}
