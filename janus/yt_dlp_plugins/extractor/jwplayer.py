from yt_dlp.extractor.common import InfoExtractor
from urllib import parse
import sys


class JWPlayerIE(InfoExtractor):
    _VALID_URL = False

    def _extract_from_webpage(self, url, webpage):
        video_id = url
        jsn = next(self._yield_json_ld(webpage, video_id, default={}), {})
        embedUrl = jsn.get("embedUrl", None)
        if embedUrl is None:
            return

        title = jsn["name"]
        urlparts = parse.urlsplit(url)
        referer = parse.urlunsplit((urlparts.scheme, urlparts.netloc, '', '', ''))
        webpage = self._download_webpage(embedUrl, video_id, fatal=False, headers={"referer": referer})
        if webpage is None:
            return

        self.report_extraction(embedUrl)
        video_url = self._search_regex(r"video_url:\s*'([^']+)", webpage, "video_url")
        resolution = self._search_regex(r"video_url_text:\s*'([^']+)", webpage, "video_url_text")
        if video_url is None:
            return

        formats = [dict(url=video_url, quality=int(resolution[:-1]), resolution=resolution, ext="mp4")]

        video_url = self._search_regex(r"video_alt_url:\s*'([^']+)", webpage, "video_alt_url")
        resolution = self._search_regex(r"video_alt_url_text:\s*'([^']+)", webpage, "video_alt_url_text")
        if video_url is not None:
            formats.append(dict(url=video_url, quality=int(resolution[:-1]), resolution=resolution, ext="mp4"))

        yield dict(id=video_id, title=title, formats=formats)
