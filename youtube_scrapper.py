import datetime
import re
from typing import Optional, List
from pydantic import BaseModel
from dateutil.relativedelta import relativedelta


class YoutubeScrappedVideo(BaseModel):
    id: str
    title: str
    # published_time_datetime: str
    published_time_string: str
    view_count: str
    channel_name: str
    channel_url: str
    description: str | None


class YoutubeWebCommandMetadata(BaseModel):
    url: str | None


class YoutubeCommandMetadata(BaseModel):
    webCommandMetadata: YoutubeWebCommandMetadata


class YoutubeBrowseEndpoint(BaseModel):
    browseId: str
    canonicalBaseUrl: str


class YoutubeNavigationEndpoint(BaseModel):
    clickTrackingParams: str
    commandMetadata: YoutubeCommandMetadata
    browseEndpoint: YoutubeBrowseEndpoint


class YoutubeRunsText(BaseModel):
    text: str | None


class YoutubeRunsNavigationEndpoint(BaseModel):
    navigationEndpoint: YoutubeNavigationEndpoint | None


class YoutubeRuns(BaseModel):
    runs: list[YoutubeRunsText]


class YoutubeLongBylineTextRuns(BaseModel):
    runs: list[YoutubeRunsNavigationEndpoint]


class YoutubePublishedTimeText(BaseModel):
    simpleText: str


class YoutubeViewCountText(BaseModel):
    simpleText: str


class YoutubedetailedMetaSnippet(BaseModel):
    snippetText: YoutubeRuns


class YoutubeScrapeResult(BaseModel):
    videoId: str
    title: YoutubeRuns
    publishedTimeText: Optional[YoutubePublishedTimeText] = None
    viewCountText: Optional[YoutubeViewCountText] = None
    ownerText: YoutubeRuns
    longBylineText: YoutubeLongBylineTextRuns
    detailedMetadataSnippets: Optional[list[YoutubedetailedMetaSnippet]] = None

    def to_youtube_scrapping_result(self) -> YoutubeScrappedVideo:
        final_result = YoutubeScrappedVideo(
            id=self.videoId,
            title=self.title.runs[0].text,
            # published_time_datetime=(
            #     self.get_past_date(publishedTimeTextStr)
            #     if publishedTimeTextStr
            #     else None),
            published_time_string=(
                self.publishedTimeText.simpleText
                if self.publishedTimeText
                else None
            ),
            # view_count=(
            #     re.findall(r"\d+", viewCountStr.replace(".", "").replace(",", ""))[0]
            #     if viewCountStr
            #     else None
            # ),
            view_count=(
                self.viewCountText.simpleText
                if self.viewCountText
                else None
            ),
            channel_name=(
                self.ownerText.runs[0].text
                if self.ownerText
                else None
            ),
            channel_url=(
                self.longBylineText.runs[0]
                .navigationEndpoint.commandMetadata
                .webCommandMetadata.url
                if self.longBylineText
                else None
                ),
            description=(
                self.detailedMetadataSnippets[0]
                .snippetText.runs[0].text
                if self.detailedMetadataSnippets
                else None
            ),
        )
        return final_result

    @staticmethod
    def get_past_date(str_time_ago: str):

        extracted_number = re.findall(r"\d+", str_time_ago)[0]
        string_lowercase = str_time_ago.lower()
        kwargs = {}
        translate_dict = {
            "minutes": ["minute", "minutes", "minuto", "minutos"],
            "hours": ["hour", "hours", "hora", "horas"],
            "days": ["day", "days", "día", "días"],
            "weeks": ["week", "weeks", "semana", "semanas"],
            "months": ["month", "months", "mes", "meses"],
            "years": ["year", "years", "año", "años"],
        }

        keys = [
            key
            for key, value in translate_dict.items()
            if any(x in string_lowercase for x in value)
        ]

        kwargs[keys[0]] = int(extracted_number)

        if not keys:
            return "Wrong Argument format"
        else:
            date = datetime.datetime.now() - relativedelta(**kwargs)
            return str(date.date().isoformat())


class ScrappingResultList(BaseModel):
    videos: List[YoutubeScrappedVideo]
