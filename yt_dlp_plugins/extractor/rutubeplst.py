from yt_dlp.extractor.common import InfoExtractor


class RutubePlstIE(InfoExtractor):
    _VALID_URL = r'(?:https?://)?(?:www\.)?rutube\.ru/plst/(?P<id>[\d]+)/'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        # Remove JSONDecodeError blocks (quote in quotes).
        webpage = webpage.replace(r'\x', "")

        playlist = self._search_json('window.reduxState\s*=\s*', webpage, 'JSON', video_id)
        title = self._html_extract_title(webpage)
        self.report_extraction(title)

        query_name = f"getPlaylistVideos/{video_id}"
        videos = playlist['api']['queries'][query_name]['data']['results']
        urls = [self.url_result(ep['video_url'], id=ep['id'], title=ep['title'], duration=ep['duration'])
                for ep in videos]

        return self.playlist_result(urls, video_id, title, playlist_count=len(urls))
