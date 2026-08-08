from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils.networking import random_user_agent

import re
from urllib import parse


class AnyDBIE(InfoExtractor):
    # https://anidb.app/anime/<name>-<id>[?lang=eng|jpn][&movie=<id>]
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?anidb\.app)/anime/[^/]+-(?P<id>[\d]+)'

    def _extract_episode(self, url, video_id, urlquery, headers):
        webpage = self._download_webpage(url, video_id, headers=headers)
        title = self._html_extract_title(webpage)
        self.report_extraction("Download languages")
        video_id = urlquery['movie']
        jsn = self._download_json(f"https://anidb.app/api/frontend/episode/{video_id}/languages", video_id, headers=headers)
        lang = urlquery.get('lang', None)
        if lang is None:
            jsnpart = jsn['languages'][0]
        else:
            try:
                jsnpart = next(filter(lambda x: x['code'] == lang, jsn['languages']))
            except StopIteration:
                jsnpart = jsn['languages'][0]
                self.report_extraction(f"Wrong lang '{lang}', select the first available '{jsnpart['code']}'")

        url = jsnpart['embed_url']

        self.report_extraction("Download m3u8")
        webpage = self._download_webpage(url, video_id, headers=headers)
        hlsurl = self._html_search_regex(r"sources:\s*\[{\s*file:\s*'([^']+)", webpage, "Find hls url")
        episode = urlquery.get('episode', 0)
        return {
                'formats': [{'url': hlsurl}],
                'id': video_id,
                'title': f"{title} - {episode}",
                'episode_number': int(episode),
        }

    def _list_episodes(self, purl, video_id, urlquery, headers):
        webpage = self._download_webpage(purl.geturl(), video_id, headers=headers)
        title = self._html_extract_title(webpage)
        self.report_extraction("Download episodes")
        jsn = self._download_json(f"https://anidb.app/api/frontend/anime/{video_id}/episodes", video_id, headers=headers)

        def parse_episode(episode):
            newitems = {'movie': ep['id'], 'episode': ep['number'], **urlquery}
            q = parse.urlencode(newitems)
            return self.url_result(purl._replace(query=q).geturl(), title=f"{title} - {ep['number']}", ie='AnyDB')

        if 'episode' in urlquery:
            n = int(urlquery['episode'])
            ep = next(filter(lambda x: x['number'] == n, jsn['episodes']))
            return parse_episode(ep)

        urls = []
        for ep in jsn['episodes']:
            newitems = {'movie': ep['id'], 'episode': ep['number'], **urlquery}
            q = parse.urlencode(newitems)
            urls.append(self.url_result(purl._replace(query=q).geturl(), title=f"{title} - {ep['number']}", ie='AnyDB'))

        return self.playlist_result(urls, video_id, title, playlist_count=len(urls))

    def _real_extract(self, url):
        headers={'referer': url, 'user-agent': random_user_agent()}

        video_id = self._match_id(url)
        purl = parse.urlparse(url)
        items = dict(parse.parse_qsl(purl.query))
        if 'movie' in items:
            return self._extract_episode(url, video_id, items, headers)

        return self._list_episodes(purl, video_id, items, headers)
