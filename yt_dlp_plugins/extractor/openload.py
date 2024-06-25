from yt_dlp.extractor.common import InfoExtractor


class OpenLoadIE(InfoExtractor):
    _VALID_URL = r'(?:https?://)?(?:www\.)?.+?/detail.php\?vid=(?P<id>[\dA-Z=]+?)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        url = self._html_search_regex(r'"file":\s*"(http.*?openload[^"]+)"', webpage, video_id)
        self.report_extraction(video_id)

        # to avoid 'direct' flag for mpv
        urls = [self.url_result(url)]
        return self.playlist_result(urls, video_id, playlist_count=1)
