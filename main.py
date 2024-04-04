import pprint
from bs4 import BeautifulSoup
from pydantic import ValidationError
import requests
import json
import logging

from youtube_scrapper import (
    ScrappingResultList,
    YoutubeScrappedVideo,
    YoutubeScrapeResult,
)

logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)


class YoutubeScraping:

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

    def getYoutubeScrapeResults(
            self,
            search_term: str,
            n: int
            ) -> YoutubeScrapeResult:

        youtube_url = "https://www.youtube.com/results?search_query="
        video_url = youtube_url + search_term

        response = requests.request("GET", video_url)
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.find_all("body")[0]
        scripts = body.find_all("script")
        data = json.loads(scripts[13].string[20:-1])

        scraped_results: list[YoutubeScrappedVideo] = []

        try:
            video_renderer_list = list(self.findkeys(data, "videoRenderer"))
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

    def run_interaction(self, search_term: str, n: int) -> ScrappingResultList:
        scrapped_videos = self.getYoutubeScrapeResults(search_term, n)
        list_scraped_videos = ScrappingResultList(videos=scrapped_videos)
        return list_scraped_videos


sc = YoutubeScraping().run_interaction("trump", 5)
pp.pprint(sc)
