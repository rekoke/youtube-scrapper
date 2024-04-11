import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from pydantic import ValidationError
import requests
import pprint
import json
import logging

from youtube_scrapper import (
    ScrappingResultList,
    YoutubeScrappedVideo,
    YoutubeScrapeResult,
)

logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)
load_dotenv()


class YoutubeScraping:

    host = "brd.superproxy.io"
    port = 22225
    username = os.getenv("PROXY_USERNAME")
    password = os.getenv("PROXY_PASSWORD")

    def findkeys(self, node, kv):
        if isinstance(node, list):
            for i in node:
                for x in self.findkeys(i, kv):
                    yield x
        elif isinstance(node, dict):
            if kv in node:
                yield node[kv]
            for j in node.values():
                for x in self.findkeys(j, kv):
                    yield x

    def build_proxies(self, country):
        proxy_url = "https://{}-country-{}:{}@{}:{}".format(
            self.username, country, self.password, self.host, self.port
        )
        proxies = {"http": proxy_url, "https": proxy_url}
        return proxies

    def get_html(self, search_term, country):
        proxies = self.build_proxies(country)
        lang = country
        video_url = "https://www.youtube.com/results?search_query="\
                    "{}&hl={}&gl={}&persist_hl=1&persist_gl=1".format(
                     search_term, lang, country
                    )

        print(video_url)
        try:
            response = requests.get(
                video_url,
                proxies=proxies)
            soup = BeautifulSoup(response.text, "html.parser")
            return soup
        except OSError as e:
            print(e)

    def getYoutubeScrapeResults(self, search_term: str, country: str, n: int):
        htmlBright = self.get_html(search_term, country)
        bodyBright = htmlBright.find_all("body")[0]
        scriptsBright = bodyBright.find_all("script")
        dataBright = json.loads(scriptsBright[13].string[20:-1])

        scraped_results: list[YoutubeScrappedVideo] = []

        try:
            video_renderer_list = list(
                self.findkeys(dataBright, "videoRenderer"))
        except Exception:
            logger.error("videoRenderer key not found in the script")

        try:
            for video in video_renderer_list[:n]:
                scraped_results.append(
                    YoutubeScrapeResult(**video).to_youtube_scrapping_result()
                )
            return scraped_results

        except ValidationError as e:
            logger.error(
                f"Unable to parse Pydantic models\
                from Youtube response.\n\n{e}"
            )
        return scraped_results

    def run_interaction(
            self,
            search_term: str,
            country: str,
            n: int) -> ScrappingResultList:
        scrapped_videos = self.getYoutubeScrapeResults(search_term, country, n)
        return scrapped_videos


sc = YoutubeScraping().run_interaction("israel", "es", 20)
pp.pprint(sc)
