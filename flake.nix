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
        packages.default = pkgs.writeShellApplication {
          name = "run-trend";
          runtimeInputs = [ pythonEnv ];
          text = ''
            cd ${./.}
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
          ];

          shellHook = ''
            echo "Running Progress Tracker Development Environment"
            echo "Python: ${pythonEnv}/bin/python --version"
            echo ""
            echo "Available commands:"
            echo "  python -m run_trend.main - Run the application"
            echo "  pytest tests/            - Run tests"
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
