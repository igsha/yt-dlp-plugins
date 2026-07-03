{
  description = "A yt-dlp plugins collection";

  inputs.nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";

  outputs = { self, nixpkgs }: let
    overlay = final: prev: {
      pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
        (pfinal: pprev: {
          yt-dlp-plugins = pfinal.callPackage ./. { };
        })
      ];
    };
    pkgs = import nixpkgs {
      system = "x86_64-linux";
      overlays = [ overlay ];
    };
  in {
    overlays.default = overlay;
    packages.x86_64-linux = {
      yt-dlp-plugins = pkgs.python3Packages.yt-dlp-plugins;
      default = self.packages.x86_64-linux.yt-dlp-plugins;
    };
  };
}
