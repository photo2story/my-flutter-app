{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python312
    pkgs.python38Packages.virtualenv
    pkgs.git
    pkgs.openssl
    pkgs.curl
    pkgs.wget
  ];

  shellHook = ''
    echo "Welcome to the development environment!"
    source .venv/bin/activate
  '';
}
