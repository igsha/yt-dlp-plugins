from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils.networking import random_user_agent
import re, base64, json, sys


class ObrutIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?\w+\.obrut\.show)/embed/(?P<id>.+)'
    _TESTS = [{
        'url': 'https://54243ba5.obrut.show/embed/AO/kinopoisk/gNxcDNyMDN/?season=1&episode=1',
        'info_dict': {
            'id': 'AO/kinopoisk/gNxcDNyMDN/?season=1&episode=1',
            'episode_number': 1,
            'formats': [{
                'url': r'https://cdn-54243ba5.obrut.show/stream/AO/.*',
                'ext': 'mp4',
                'protocol': 'https'
            }]
        }
    }]

    @staticmethod
    def _get_best_resolution_url(description):
        url, res = None, 0
        for s in description.split(','):
            m = re.match(r"\[(\d+)p\](.+)", s)
            if m is not None and int(m[1]) > res:
                url, res = m[2], int(m[1])

        return url

    def _real_extract(self, url):
        video_id = self._match_id(url)
        domain = self._search_regex(self._VALID_URL, url, "domain", group='domain')
        headers={'referer': domain, 'user-agent': random_user_agent()}

        webpage = self._download_webpage(url, video_id, headers=headers)
        title = self._html_extract_title(webpage)

        data = self._html_search_regex(r'new Player\("#2t([^"]+)"', webpage, video_id)
        data = re.sub(r'//[^=]+=', '', data) # remove `//ci9yL3I=`-like parts
        data = base64.b64decode(data + '=' * (-len(data) % 4)) # fix padding
        data = json.loads(data)

        urls = []
        for season in data['file']:
            for episode in season['folder']:
                formats = []
                hashset = set()
                result = dict(id=episode['title'], season=season['title'], episode=episode['title'])
                for translation in episode['folder']:
                    result['title'] = f"{title} - {translation['t1']}"
                    url = self._get_best_resolution_url(translation['file'])
                    lang = translation['title']
                    formatid = sum(map(ord, lang))
                    while formatid in hashset:
                        formatid += 1

                    hashset.add(formatid)
                    formats.append(dict(ext='mp4', url=url, format_id=str(formatid), language=lang))

                result['formats'] = formats
                urls.append(result)

        return self.playlist_result(urls, video_id, title, playlist_count=len(urls))
