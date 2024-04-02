import re
from typing import Optional, List
from pydantic import BaseModel


class YoutubeScrappedVideo(BaseModel):
    id: str
    title: str
    published_time: str
    view_count: str
    channel_name: str
    description: str | None


class YoutubeRunsText(BaseModel):
    text: str | None


class YoutubeRuns(BaseModel):
    runs: list[YoutubeRunsText] | None


class YoutubePublishedTimeText(BaseModel):
    simpleText: str


class YoutubeViewCountText(BaseModel):
    simpleText: str


class YoutubedetailedMetaSnippetItem(BaseModel):
    snippetText: YoutubeRuns


class YoutubeScrapeResult(BaseModel):
    videoId: str
    title: YoutubeRuns
    publishedTimeText: Optional[YoutubePublishedTimeText] = None
    viewCountText: Optional[YoutubeViewCountText] = None
    ownerText: YoutubeRuns
    detailedMetaSnippets: Optional[list[YoutubedetailedMetaSnippetItem]] = None

    def to_youtube_scrapping_result(self) -> YoutubeScrappedVideo:
        return YoutubeScrappedVideo(
            id=self.videoId,
            title=self.title.runs[0].text,
            published_time=self.publishedTimeText.simpleText,
            view_count=re.findall(
                "\d+", self.viewCountText.simpleText.replace(".", "")
            )[0],
            channel_name=self.ownerText.runs[0].text,
            description=(
                self.detailedMetaSnippets[0].snippetText.runs[0].text
                if self.detailedMetaSnippets
                else None
            ),
        )


class ScrappingResultList(BaseModel):
    videos: List[YoutubeScrappedVideo]
