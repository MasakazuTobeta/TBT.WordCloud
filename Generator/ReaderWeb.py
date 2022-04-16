## coding: UTF-8
import urllib.request as req
from bs4 import BeautifulSoup
from . import GenerateWordCloud

class GenerateFromWeb(GenerateWordCloud):
    def __init__(self, *args, url, depth, **kwargs):
        super().__init__(*args, **kwargs)
        self.url             = str(url)
        self.depth           = int(depth)
        self.read_text_lines = self.get_text
    
    @staticmethod
    def get_host_name(url):
        return '/'.join(url.split('/')[:4])
    
    @staticmethod
    def get_page_text_only(soup):
        for script in soup(["script", "style"]):
            script.decompose()
        text  = soup.get_text()
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        return lines

    def get_text(self, url=None, host=None, depth=None):
        if url is None:
            self.done = []
            url = self.url
        if not url.startswith('http'):
            url = 'http://'+url
        if host is None:
            host = self.get_host_name(url)
        if depth is None:
            depth = self.depth
        if url.startswith(host) and (url not in self.done):
            try:
                res  = req.urlopen(url)
                soup = BeautifulSoup(res, "html.parser")
                for line in self.get_page_text_only(soup):
                    yield line
                self.done.append(url)
                if depth>0:
                    for aa in soup.find_all("a"):
                        link = aa.get("href")
                        for line in self.get_text(url=link, host=host, depth=depth-1):
                            yield line
            except:
                pass