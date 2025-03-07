{ lib, buildPythonPackage, setuptools, lxml }@args:

let
  toml = builtins.fromTOML (builtins.readFile ./pyproject.toml);
in buildPythonPackage {
  pname = "yt-dlp-plugins";
  version = toml.project.version;
  pyproject = true;

  src = ./.;

  build-system = builtins.map (x: args.${x}) toml.build-system.requires;
  dependencies = builtins.map (x: args.${x}) toml.project.dependencies;

  meta = {
    homepage = toml.project.urls.Homepage;
    description = toml.project.description;
    license = lib.licenses.free;
    maintainers = with lib.maintainers; [ igsha ];
    platforms = lib.platforms.unix;
  };
}
