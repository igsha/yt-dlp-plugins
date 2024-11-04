from yt_dlp.extractor.common import InfoExtractor


class OpenLoadIE(InfoExtractor):
    _VALID_URL = False

    def _extract_from_webpage(self, url, webpage):
        video_id = url
        url = self._html_search_regex(r'"file":\s*"(http.*?openload[^"]+)"', webpage, video_id, default=None)
        if url is None:
            return

        self.report_extraction(video_id)

        # to avoid 'direct' flag for mpv
        urls = [self.url_result(url)]
        yield self.playlist_result(urls, video_id, playlist_count=1)
