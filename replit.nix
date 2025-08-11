{ pkgs }: {
  deps = [
    pkgs.python311Full
    pkgs.python311Packages.pip
  ];
  shellHook = ''
    pip install -r requirements.txt
  '';
}
