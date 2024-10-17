from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils.networking import random_user_agent
import re, base64, json, sys
from urllib import parse


class ObrutIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?\w+\.obrut\.show)/embed/(?P<id>.+)'
    _TESTS = [{
        'url': 'https://54243ba5.obrut.show/embed/AO/kinopoisk/gNxcDNyMDN/?season=1&episode=1',
        'info_dict': {
            'id': 'AO/kinopoisk/gNxcDNyMDN/?season=1&episode=1',
            'title': 'Расхитительница гробниц: Легенда о Ларе Крофт - S01E01 - Один шаг',
            'episode_number': 1,
            'formats': [{
                'url': r'https://cdn-54243ba5.obrut.show/stream/AO/.*',
                'ext': 'unknown_video',
                'protocol': 'https'
            }]
        }
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        domain = self._search_regex(self._VALID_URL, url, "domain", group='domain')
        headers={'referer': domain, 'user-agent': random_user_agent()}

        webpage = self._download_webpage(url, video_id, headers=headers)
        title = self._html_extract_title(webpage)

        data = self._html_search_regex(r'new Player\("#2t([^"]+)"', webpage, video_id)
        data = re.sub(r'//[^=]+=', '', data) # remove `//ci9yL3I=`-like parts
        data = base64.b64decode(data + '=' * (-len(data) % 4)) # fix padding

        jsn = json.loads(data)
        desc = jsn['file'][0] # Use the first translation
        title = title + " - " + desc['t1']
        params = dict(parse.parse_qsl(parse.urlparse(url).query))

        result = dict(id=video_id, title=title, episode_number=int(params['episode']))
        result['formats'] = [{'url': url, 'quality': int(quality)}
                             for quality, url in re.findall(r'\[(\d+)p\]([^,]+)', desc['file'])]

        return result
