from yt_dlp.extractor.common import InfoExtractor


class TobacoIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?api\.tobaco\.ws)/embed/movie/(?P<id>[\d]+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        title = self._html_extract_title(webpage)
        seasons = self._search_json('seasons:', webpage, 'JSON', video_id, contains_pattern=r'\[{(?s:.+)}\]',
                                    end_pattern='},')

        self.report_extraction(title)
        # dash or hls
        urls = [self.url_result(ep['hls'], title=ep['title'], duration=ep['duration'])
                for season in seasons
                for ep in season['episodes']]

        return self.playlist_result(urls, video_id, title, playlist_count=len(urls))
