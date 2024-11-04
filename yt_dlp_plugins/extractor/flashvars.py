from yt_dlp.extractor.common import InfoExtractor


class FlashVarsIE(InfoExtractor):
    _VALID_URL = False

    def _extract_from_webpage(self, url, webpage):
        video_id = url
        body = self._html_search_regex(r"var flashvars = {([^}]+)};", webpage, video_id, default=None)
        if body is None:
            return

        video_id = self._search_regex(r"video_id:\s*'(\d+)'", body, video_id)
        self.report_extraction(video_id)

        formats = [{}]
        formats[0]['url'] = video_url = self._search_regex(r"video_url:\s*'([^']+)'", body, video_id)
        video_url_text = self._search_regex(r"video_url_text:\s*'([^']+)'", body, video_id)
        formats[0]['quality'] = int(video_url_text.replace('p', ''))

        video_url = self._search_regex(r"video_alt_url:\s*'([^']+)'", body, video_id, default=None)
        if video_url is not None:
            formats.append({})
            formats[1]['url'] = video_url
            video_url_text = self._search_regex(r"video_alt_url_text:\s*'([^']+)'", body, video_id)
            formats[1]['quality'] = int(video_url_text.replace('p', ''))

        title = self._html_extract_title(webpage)
        yield dict(id=video_id, title=title, formats=formats)
