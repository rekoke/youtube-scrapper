from bs4 import BeautifulSoup
from pydantic import ValidationError
import requests
import json
import logging

from youtube_api import YoutubeScrappedVideo, YoutubeScrapeResult

logger = logging.getLogger(__name__)

video_id = "burton"
video_url = "https://www.youtube.com/results?search_query=" + video_id
response = requests.request("GET", video_url)
soup = BeautifulSoup(response.text, "html.parser")
body = soup.find_all("body")[0]
scripts = body.find_all("script")

result = json.loads(scripts[13].string[20:-1])

estimatedResults = result['estimatedResults']


def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x


video_renderer_list = list(findkeys(result, 'videoRenderer'))
scrape_results: list[YoutubeScrappedVideo] = []


try:
    for video in video_renderer_list:
        scrape_results.append(YoutubeScrapeResult(**video).to_youtube_scrapping_result())
except ValidationError as e:
    logger.error(f"Unable to parse Pydantic models from Youtube response.\n\n{e}")

print(scrape_results)
