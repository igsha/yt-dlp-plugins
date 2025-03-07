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
      yt-dlp-with-plugins = let
        # extract appropriate python3Packages
        pp = with builtins; head (filter (x: x.pname == "python3") final.yt-dlp.propagatedBuildInputs);
      in prev.symlinkJoin {
        name = "yt-dlp-with-plugins";
        paths = [ final.yt-dlp ];
        buildInputs = [ prev.makeWrapper ];
        postBuild = ''
          wrapProgram $out/bin/yt-dlp \
            --prefix PYTHONPATH : "${toPathWithSep final.${pp.pythonAttr}.pkgs.yt-dlp-plugins}"
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
      default = self.packages.x86_64-linux.yt-dlp-with-plugins;
    };
    apps.x86_64-linux.default = {
      type = "app";
      program = "${self.packages.x86_64-linux.yt-dlp-with-plugins}/bin/yt-dlp";
    };
  };
}
