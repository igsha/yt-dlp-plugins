from yt_dlp.extractor.common import InfoExtractor
import json, datetime, sys


class RutubeShortsIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?rutube\.ru)/shorts/(?P<id>[\d\w]+)/?'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        domain = self._search_regex(self._VALID_URL, url, "domain", group='domain')

        return self.url_result(url=f"{domain}/video/{video_id}/", ie='Rutube')
