from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.extractor import IwaraIE

import random
from urllib.parse import urlparse


class IwaraReplacerIE(InfoExtractor):
    _VALID_URL = IwaraIE._VALID_URL
    _VALID_SERVERS = ['silverwolf', 'pela', 'mikoto', 'hime']
    _REPLACE_SERVERS = ['silverwolf', 'pela']

    def _real_extract(self, url):
        iwara_ie = IwaraIE()
        iwara_ie.set_downloader(self._downloader)
        result = iwara_ie.extract(url)
        for fmt in result['formats']:
            a = urlparse(fmt['url'])
            names = a.netloc.split('.')
            ischanged = False
            if not names[0] in self._VALID_SERVERS:
                names[0] = random.choice(self._REPLACE_SERVERS)
                self.write_debug(f"Replace {fmt['url']} by {names[0]}")
                ischanged = True

            if ischanged:
                fmt['url'] = a._replace(netloc='.'.join(names)).geturl()

        return result
