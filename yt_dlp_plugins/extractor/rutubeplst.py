from yt_dlp.extractor.common import InfoExtractor
import json, datetime, sys


class RutubePlstIE(InfoExtractor):
    _VALID_URL = r'(?P<domain>(?:https?://)?(?:www\.)?rutube\.ru)/plst/(?P<id>[\d]+)/?'
    _TESTS = [{
        'url': 'https://rutube.ru/plst/119828/',
        'info_dict': {
            "playlist_count": 28,
            "id": "119828",
            "title": "C++ базовый курс, MIPT – смотреть онлайн все 28 видео от C++ базовый курс, MIPT в хорошем качестве на RUTUBE",
            "entries": [{
                "id": "fdf7802b6a9d8b79cc43c05efbdb0863",
                "title": "Базовый курс C++ (MIPT, ILab). Lecture 1. Scent of C++.",
                "uploader": "C++ лекции на русском языке",
                "uploader_id": "10218561",
                "timestamp": 1646179900
            }]
        }
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        domain = self._search_regex(self._VALID_URL, url, "domain", group='domain')

        webpage = self._download_webpage(url, video_id)
        title = self._html_extract_title(webpage)
        self.report_extraction(title)

        results = []
        data_url = f'{domain}/api/playlist/custom/{video_id}/videos/'
        while data_url != None:
            data = self._download_webpage(data_url, video_id)
            jsn = json.loads(data)
            for item in jsn['results']:
                results.append(dict(url=item['video_url'],
                                    id=item['id'],
                                    title=item['title'],
                                    duration=item['duration'],
                                    date=datetime.datetime.fromisoformat(item['publication_ts'])))

            data_url = jsn['next']

        urls = [self.url_result(x['url'], id=x['id'], title=x['title'], duration=x['duration'])
                for x in sorted(results, key=lambda t: t['date'])]

        return self.playlist_result(urls, video_id, title, playlist_count=len(urls))
