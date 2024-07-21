{ lib, buildPythonPackage, setuptools, lxml }:

buildPythonPackage {
  pname = "yt-dlp-plugins";
  version = "2024.07.21";
  format = "pyproject";

  src = ./.;

  buildInputs = [ setuptools ]; # build-system
  propagatedBuildInputs = [ lxml ]; # dependencies

  meta = {
    homepage = "https://github.com/igsha/yt-dlp-plugins";
    description = "A yt-dlp plugins collection";
    license = lib.licenses.free;
    maintainers = with lib.maintainers; [ igsha ];
    platforms = lib.platforms.unix;
  };
}
