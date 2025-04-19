from yt_dlp.extractor.common import InfoExtractor


class IFrameIE(InfoExtractor):
    _VALID_URL = False

    def _extract_from_webpage(self, url, webpage):
        video_id = url
        iframe = self._html_search_regex(r'<iframe src="([^"]+)"', webpage, "iframe", default=None)
        if iframe is None:
            return

        self.report_extraction(video_id)

        # to avoid 'direct' flag for mpv
        urls = [self.url_result(iframe)]
        yield self.playlist_result(urls, video_id, playlist_count=1)
