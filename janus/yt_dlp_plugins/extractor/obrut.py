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
    def _get_series_playlist(folder, title, fmttag):
        urls = []
        for season in folder:
            for episode in season['folder']:
                desc = ObrutIE._get_video_formats(episode['folder'], title, fmttag,
                                                  id=episode['title'],
                                                  season=season['title'],
                                                  episode=episode['title'])
                urls.append(desc)

        return urls

    @staticmethod
    def _get_video_formats(folder, title, fmttag, **kwargs):
        hashset = set()
        formats, newtitle = [], title
        for translation in folder:
            if len(translation.get('t1', "")) > 0:
                newtitle = f"{title} - {translation['t1']}"

            for s in translation['file'].split(','):
                m = re.match(r"\[(\d+p)\](.+)", s)
                if m is None:
                    continue

                res, url = m[1], m[2]
                lang = translation['title']
                formatid = sum(map(ord, lang + res))
                while formatid in hashset:
                    formatid += 1

                hashset.add(formatid)
                formats.append(dict(ext='mp4', url=url, resolution=res,
                                    format_id=str(formatid), language=lang,
                                    title=f"{newtitle} [{lang}]"))

        if fmttag is not None:
            for tag in fmttag:
                for fmt in formats:
                    if fmt['format_id'] == tag:
                        return dict(**fmt, **kwargs, _type='url_transparent')

        return dict(formats=formats, title=newtitle, **kwargs)

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

        ftag = self._search_regex(r"ytdl-format=(?P<tag>[\d,]+)", video_id, "formattag", default=None, group="tag")
        if ftag is not None:
            ftag = ftag.split(',')

        if data['file'][0].get('folder') is not None:
            urls = self._get_series_playlist(data['file'], title, ftag)
            return self.playlist_result(urls, video_id, title, playlist_count=len(urls))
        else:
            return self._get_video_formats(data['file'], title, ftag, id=video_id)
