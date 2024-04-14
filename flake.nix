{
  description = "A yt-dlp plugins collection";

  inputs.nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";

  outputs = { self, nixpkgs }: let
    getDeps = x: map (p: "${p}/${p.pythonModule.sitePackages}") ([ x ] ++ x.propagatedBuildInputs);
    toPathWithSep = x: pkgs.lib.concatStringsSep ":" (getDeps x);
    overlay = final: prev: {
      pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
        (pfinal: pprev: {
          yt-dlp-plugins = pfinal.callPackage ./. { };
        })
      ];
      yt-dlp-with-plugins = prev.symlinkJoin {
        name = "yt-dlp-with-plugins";
        paths = [ prev.yt-dlp ];
        buildInputs = [ prev.makeWrapper ];
        # Somehow need to get python from yt-dlp
        postBuild = ''
          wrapProgram $out/bin/yt-dlp \
            --prefix PYTHONPATH : "${toPathWithSep final.python3Packages.yt-dlp-plugins}"
        '';
      };
    };
    pkgs = import nixpkgs {
      system = "x86_64-linux";
      overlays = [ overlay ];
    };
  in {
    overlays.default = overlay;
    packages.x86_64-linux = {
      yt-dlp-plugins = pkgs.python3Packages.yt-dlp-plugins;
      yt-dlp-with-plugins = pkgs.yt-dlp-with-plugins;
      default = self.packages.x86_64-linux.yt-dlp-plugins;
    };
    apps.x86_64-linux.default = {
      type = "app";
      program = "${self.packages.x86_64-linux.yt-dlp-with-plugins}/bin/yt-dlp";
    };
  };
}
