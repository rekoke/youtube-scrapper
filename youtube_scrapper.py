import datetime
import re
from typing import Optional, List
from pydantic import BaseModel
from dateutil.relativedelta import relativedelta


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
        publishedTimeTextStr = self.publishedTimeText.simpleText
        viewCountStr = self.viewCountText.simpleText

        return YoutubeScrappedVideo(
            id=self.videoId,
            title=self.title.runs[0].text,
            published_time=self.get_past_date(publishedTimeTextStr),
            view_count=re.findall(r"\d+", viewCountStr.replace(".", ""))[0],
            channel_name=self.ownerText.runs[0].text,
            description=(
                self.detailedMetaSnippets[0].snippetText.runs[0].text
                if self.detailedMetaSnippets
                else None
            ),
        )

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
