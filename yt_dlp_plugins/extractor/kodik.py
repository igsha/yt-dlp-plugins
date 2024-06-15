from yt_dlp.extractor.common import InfoExtractor
from urllib import parse
import re, json, sys, base64
from lxml import etree


class KodikIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?(kodik|aniqit|anivod)\.[^/]+)/ftor\?(?P<item>.+)'
    _decode_table = {
            **{c: c + 13 if c < ord('N') else c - 13 for c in range(ord('A'), ord('Z') + 1)},
            **{c: c + 13 if c < ord('n') else c - 13 for c in range(ord('a'), ord('z') + 1)}}

    @staticmethod
    def __decode(data):
        decoded = base64.b64decode(data.translate(__class__._decode_table))
        return re.sub(r'^//', 'https://', decoded.decode())

    def _real_extract(self, url):
        item = dict(parse.parse_qsl(re.search(self._VALID_URL, url).group('item')))
        webpage = self._download_webpage(url, item['id'])
        title = item['title'] if 'title' in item else 'title'
        episode = int(item['episode']) if 'episode' in item else 0
        jsn = json.loads(webpage)
        result = dict(id=item['id'], title=title, episode_number=episode)
        if 'link' in jsn:
            result['url'] = jsn['link']
        else:
            video_urls = jsn['links']
            qualities = sorted(video_urls.keys(), key=int, reverse=True)
            result['formats'] = [{'url': self.__decode(video_urls[k][0]['src']), 'quality': int(k)}
                                 for k in qualities]

        return result


class KodikListIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?(kodik|aniqit|anivod)\.[^/]+)/(?P<type>(serial?|season))/(?P<id>[-\w/]+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        domain = re.search(self._VALID_URL, url).group('domain')

        webpage = self._download_webpage(url, video_id, headers={'referer': domain})
        t = etree.HTML(webpage)
        title = t.xpath("//title/text()")[0]
        items = t.xpath("//div[@class='serial-series-box']/*/option")

        self.report_extraction(title)
        urls = []
        for item in items:
            # episode and title is a fake arguments
            params = {k:item.get(v) for k, v in [('id', 'data-id'), ('hash', 'data-hash'), ('episode', 'value')]}
            params['title'] = title + " - " + item.get('data-title')
            params['type'] = 'seria'
            urls.append(self.url_result(f"{domain}/ftor?{parse.urlencode(params)}", ie=KodikIE.ie_key(), title=item.get('data-title')))

        return self.playlist_result(urls, video_id, title, playlist_count=len(urls))
