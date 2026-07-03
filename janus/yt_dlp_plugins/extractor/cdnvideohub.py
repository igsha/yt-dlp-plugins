from yt_dlp.extractor.common import InfoExtractor
from urllib import parse


class CdnVideoHubListIE(InfoExtractor):
    # https://plapi.cdnvideohub.com/api/v1/player/sv/playlist?pub=<pub>&aggr=<aggr>&id=<id>[&dubbing_code=<dubbing>]
    _VALID_URL = r'https://(?:www\.)?plapi.cdnvideohub.com/api/v1/player/sv/playlist\?(?P<items>.+)'

    def _real_extract(self, url):
        items = dict(parse.parse_qsl(parse.urlparse(url).query))
        lst = self._download_json(url, items['pub'])
        title = lst['titleName']
        self.report_extraction(title)
        dubbing_code = items.get('dubbing_code', lst['items'][0].get('voiceStudio', 'voiceType'))
        urls = []
        for item in filter(lambda x: x.get('voiceStudio', 'voiceType') == dubbing_code, lst['items']):
            stitle = f"{title} - {item['season']}-{item['episode']}"
            urls.append(self.url_result(f"https://plapi.cdnvideohub.com/api/v1/player/sv/video/{item['vkId']}", ie=CdnVideoHubIE.ie_key(), title=stitle))

        return self.playlist_result(urls, items['pub'], title, playlist_count=len(urls))


class CdnVideoHubIE(InfoExtractor):
    # https://plapi.cdnvideohub.com/api/v1/player/sv/video/<id>
    _VALID_URL = r'https://(?:www\.)?plapi.cdnvideohub.com/api/v1/player/sv/video/(?P<id>\d+)'

    def _real_extract(self, url):
        ident = self._match_id(url)
        sources = self._download_json(url, ident)
        sources = sources['sources']
        quality = next(iter(sources))
        for q in ["hlsUrl", "dashUrl"]:
            if q in sources and sources[q] != "":
                quality = q
                break

        self.report_extraction(f"Extract {quality}")
        url = sources[quality]
        protocol = None
        if quality.startswith("hls"):
            protocol = "m3u8_native"
        elif quality.startswith("dash"):
            protocol = "http_dash_segments"

        return self.url_result(url, protocol=protocol)
