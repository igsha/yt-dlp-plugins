from yt_dlp.extractor.common import InfoExtractor
from urllib import parse
import re, json, sys, base64
from lxml import etree


class KodikIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?(kodik|aniqit|anivod)\.[^/]+)/(?P<type>(serial?|season|video|uv))/(?P<id>[-\w/]+)'
    _decode_table = {
            **{c: c + 13 if c < ord('N') else c - 13 for c in range(ord('A'), ord('Z') + 1)},
            **{c: c + 13 if c < ord('n') else c - 13 for c in range(ord('a'), ord('z') + 1)}}

    @staticmethod
    def __decode(data):
        decoded = base64.b64decode(data.translate(__class__._decode_table))
        return re.sub(r'^//', 'https://', decoded.decode())

    def __getter(self, domain, video_type, title, item):
        video_id = item.get('data-id')
        video_hash = item.get('data-hash')
        video_value = item.get('value')
        video_title = item.get('data-title')

        params = {'type': video_type, 'id': video_id, 'hash': video_hash}
        formdata = parse.urlencode(params).encode()
        webpage = self._download_webpage(f"{domain}/ftor", "Kodik GetVideoInfo", data=formdata)

        jsn = json.loads(webpage)
        kwargs = dict(ie=None, video_id=video_id, video_title=f"{title} - {video_title}",
                      episode_number=int(video_value))
        if 'link' in jsn:
            url = jsn['link']
        else:
            video_urls = jsn['links']
            qualities = sorted(video_urls.keys(), key=int, reverse=True)
            kwargs['formats'] = [{'url': self.__decode(video_urls[k][0]['src']), 'quality': int(k)}
                                 for k in qualities]
            url = kwargs['formats'][0]['url']

        return self.url_result(url, **kwargs)

    def _real_extract(self, url):
        video_id = self._match_id(url)
        domain = re.search(self._VALID_URL, url).group('domain')
        video_type = re.search(self._VALID_URL, url).group('type')
        if video_type == 'serial' or video_type == 'season':
            video_type = 'seria'

        webpage = self._download_webpage(url, video_id, headers={'referer': domain})
        t = etree.HTML(webpage)
        title = t.xpath("//title/text()")[0]
        items = t.xpath("//div[@class='serial-series-box']/*/option")

        self.report_extraction(title)
        return self.playlist_result(map(lambda x: self.__getter(domain, video_type, title, x), items),
                                    video_id, title, playlist_count=len(items))
