from typing import Optional
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


class YoutubedetailedMetadataSnippetItem(BaseModel):
    snippetText: YoutubeRuns


class YoutubeScrapeResult(BaseModel):
    videoId: str
    title: YoutubeRuns
    publishedTimeText: YoutubePublishedTimeText
    viewCountText: YoutubeViewCountText
    ownerText: YoutubeRuns
    detailedMetadataSnippets: Optional[list[YoutubedetailedMetadataSnippetItem]] = None

    def to_youtube_scrapping_result(self) -> YoutubeScrappedVideo:
        return YoutubeScrappedVideo(
            id=self.videoId,
            title=self.title.runs[0].text,
            published_time=self.publishedTimeText.simpleText,
            view_count=self.viewCountText.simpleText,
            channel_name=self.ownerText.runs[0].text,
            description=(
                self.detailedMetadataSnippets[0].snippetText.runs[0].text
                if self.detailedMetadataSnippets
                else None
            ),
        )
