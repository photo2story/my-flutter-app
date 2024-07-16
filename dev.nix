{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python312
    # 다른 패키지들을 여기에 추가할 수 있습니다.
  ];

  shellHook = ''
    echo "Welcome to the development environment!"
    # 필요한 다른 셸 설정을 여기에 추가할 수 있습니다.
  '';
}
