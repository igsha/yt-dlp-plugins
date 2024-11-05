from yt_dlp.extractor.common import InfoExtractor
from urllib import parse


class JWPlayerIE(InfoExtractor):
    _VALID_URL = False

    def _extract_from_webpage(self, url, webpage):
        video_id = url
        jsn = next(self._yield_json_ld(webpage, video_id, default={}))
        embedUrl = jsn.get("embedUrl", None)
        if embedUrl is None:
            return

        title = jsn["name"]
        urlparts = parse.urlsplit(url)
        referer = parse.urlunsplit((urlparts.scheme, urlparts.netloc, '', '', ''))
        webpage = self._download_webpage(embedUrl, video_id, fatal=False, headers={"referer": referer})
        if webpage is None:
            return

        jsn = self._search_json(r"window.playlist\s*=\s*", webpage, "JSON playlist", video_id,
                                end_pattern=";", default=None)
        if jsn is None:
            return

        formats = [dict(url=s["file"], quality=int(s["label"]), ext=s["type"])
                   for s in jsn["sources"]]
        yield dict(id=video_id, title=title, formats=formats)
