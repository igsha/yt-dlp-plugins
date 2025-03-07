from yt_dlp.extractor.common import InfoExtractor
from urllib import parse
import re, json, sys, base64
from lxml import etree


class KodikIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?(kodik|aniqit|anivod)\.[^/]+)/ftor\?(?P<item>.+)'

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
            getsrc = lambda k: re.sub(r'^//', 'https://', video_urls[k][0]['src'])
            result['formats'] = [{'url': getsrc(k), 'quality': int(k)}
                                 for k in qualities]

        return result


class KodikVideoIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?:)?(?://)?(?:www\.)?(kodik|aniqit|anivod)\.[^/]+)/(video|seria)/(?P<id>[-\w/]+)(?:\?.*)?'
    _EMBED_REGEX = [rf'(?x)<iframe[^>]+src=["\'](?P<url>{_VALID_URL})']

    def _real_extract(self, url):
        video_id = self._match_id(url)
        domain = self._search_regex(self._VALID_URL, url, "domain", group='domain')

        webpage = self._download_webpage(url, video_id, headers={'referer': domain})

        title = self._html_extract_title(webpage, default="")
        translationTitle = self._search_regex(r'translationTitle\s*=\s*"([^"]+)"', webpage, "title2", default="")
        title += " - " + translationTitle

        video_type = self._search_regex(r"videoInfo\.type\s*=\s*'(?P<type>[^']+)'", webpage, "type", group='type')
        video_hash = self._search_regex(r"videoInfo\.hash\s*=\s*'(?P<hash>[^']+)'", webpage, "hash", group='hash')
        video_id = self._search_regex(r"videoInfo\.id\s*=\s*'(?P<id>[^']+)'", webpage, "id", group='id')

        self.report_extraction(video_id)

        params = dict(id=video_id, hash=video_hash, type=video_type, title=title)
        return self.url_result(f"{domain}/ftor?{parse.urlencode(params)}", ie=KodikIE.ie_key(), title=title, transparent=True)


class KodikListIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?(kodik|aniqit|anivod)\.[^/]+)/(?P<type>(serial|season))/(?P<id>[-\w/]+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        domain = self._search_regex(self._VALID_URL, url, "domain", group='domain')

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
