from yt_dlp.extractor.common import InfoExtractor
import re


class RalodeIE(InfoExtractor):
    _VALID_URL = False
    ftag = None

    # Redirects remove custom tags from url. Need to save ytdl-format tag
    @classmethod
    def suitable(cls, url):
        m = re.search(r".*[\?\&]ytdl-format=(?P<tag>\d+)", url)
        if m is not None:
            cls.ftag = m.group('tag')

        return False

    def _list_video_format(self, items, lang, domain, transl):
        for num, val in items.items():
            title = val['sname']
            index = int(val['lssort'])
            url = self._html_search_regex(r'<iframe [^>]*src="([^"]+)"', val['scode'], "iframe")
            if url.startswith("/"):
                url = domain + url

            yield dict(id=num, url=url, format_id=transl, language=lang, title=title, episode_number=index)

    def _extract_from_webpage(self, url, webpage):
        video_id = url
        domain = self._search_regex(r"(?P<domain>(?:https?://)?[^/]+)/", url, "domain", group="domain")
        jsn = self._search_json(r'RalodePlayer.init\(', webpage, 'JSON', video_id, default=None)
        if jsn is None:
            return

        urls = {}
        ftag = self._search_regex(r"ytdl-format=(?P<tag>\d+)", url, "formattag", default=None, group="tag")
        if ftag is None:
            self.write_debug("Use last saved ytdl-format tag")
            ftag = RalodeIE.ftag

        if ftag is None:
            for transl, items in jsn.items():
                for fmt in self._list_video_format(items['items'], items['name'], domain, transl):
                    index = fmt['episode_number']
                    if index in urls:
                        urls[index]['formats'].append(fmt)
                    else:
                        urls[index] = dict(id=fmt['id'], formats=[fmt], title=fmt['title'])
        else:
            items = jsn[ftag]
            for fmt in self._list_video_format(items['items'], items['name'], domain, ftag):
                urls[fmt['episode_number']] = fmt

        urls = [urls[k] for k in sorted(urls.keys())]
        title = self._html_extract_title(webpage)
        yield self.playlist_result(urls, video_id, title, playlist_count=len(urls))
