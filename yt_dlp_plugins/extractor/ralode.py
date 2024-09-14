from yt_dlp.extractor.common import InfoExtractor


class RalodeIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?ani[^\.]+\.pro)/video.php\?id=(?P<id>\d+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        src_url = self._html_search_regex(r'<iframe [^>]*src="([^"]+)"', webpage, "iframe", default=None)
        if src_url.startswith("//"):
            src_url = "https:" + src_url

        return self.url_result(src_url, id=video_id)


class RalodeListIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?ani[^\.]+\.pro)/(?P<id>[^\.]+)\.html'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        domain = self._search_regex(self._VALID_URL, url, "domain", group='domain')
        webpage = self._download_webpage(url, video_id)
        jsn = self._search_json(r'RalodePlayer.init\(', webpage, 'JSON', video_id)
        maxk = max(jsn, key=lambda k: len(jsn[k]['items']))
        urls = []
        for k, val in sorted(jsn[maxk]['items'].items()):
            urls.append(self.url_result(f"{domain}/video.php?id={val['id']}", id=val['id'], title=val['aname'], ie=RalodeIE.ie_key()))

        title = self._html_extract_title(webpage)
        return self.playlist_result(urls, video_id, title, playlist_count=len(urls))
