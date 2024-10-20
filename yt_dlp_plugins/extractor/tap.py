from yt_dlp.extractor.common import InfoExtractor
import json


class TapIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?[^/]+)/-(?P<id>[\d]+)'

    def _real_extract(self, url):
        base = 'externulls'
        video_id = self._match_id(url)
        data = self._download_webpage(f'https://store.{base}.com/facts/file/{video_id}', video_id)

        jsn = json.loads(data)
        title = jsn['file']['data'][0]['cd_value']
        key = jsn['file']['hls_resources']['fl_cdn_multi']

        return self.url_result(f'https://video.{base}.com/{key}', id=video_id, title=title)
