import time
import logging
from typing import Iterator

import praw
from praw.exceptions import RedditAPIException
from praw.models import Submission, Subreddit

from kin_txt_core.datasources.common.entities import DatasourceLink, ClassificationEntity
from kin_txt_core.datasources.common.interface import IDataSource
from kin_txt_core.datasources.settings import RedditSettings
from kin_txt_core.exceptions import RedditIsUnavailable


class RedditDatasource(IDataSource):
    _single_request_limit = 1000

    def __init__(self, client_id: str, client_secret: str, user_agent: str, settings: RedditSettings) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._user_agent = user_agent
        self._settings = settings

        self._client = praw.Reddit(
            client_id=self._client_id,
            client_secret=self._client_secret,
            user_agent=self._user_agent,
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def fetch_data(self, source: DatasourceLink) -> list[ClassificationEntity]:
        self._logger.info(f"[RedditDatasource] Fetching data from {source.source_link}")

        subreddit = self._client.subreddit(source.source_link)

        posts = []

        try:
            posts = list(self._get_posts(subreddit, source))
        except RedditAPIException as error:
            self._logger.error(f"[RedditDatasource] Reddit API error happened: {error}")
            if error.error_type == "RATELIMIT":
                raise RedditIsUnavailable(f"Reddit rate limited: {str(error)}")

            raise
        except TypeError as error:  # usually that means that there are no posts
            self._logger.warning(f"[RedditDatasource] {error}")
        except Exception as error:
            self._logger.error(f"[RedditDatasource] Error happened: {error}")
            raise

        return [
            ClassificationEntity.from_reddit_submission(post) for post in posts
        ]

    def _get_posts(self, subreddit: Subreddit, settings: DatasourceLink) -> Iterator[Submission]:
        for fetched_posts in range(0, self._settings.max_posts_per_request, self._single_request_limit):
            for post in subreddit.new(limit=self._single_request_limit):
                if post.created_utc < settings.earliest_date.timestamp():
                    return
                if post.created_utc > settings.offset_date.timestamp():
                    continue

                yield post

            time.sleep(1)  # Adjust the delay as per Reddit's rate limits

    @classmethod
    def from_settings(cls) -> "RedditDatasource":
        settings = RedditSettings()
        return cls(
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            user_agent=settings.user_agent,
            settings=settings,
        )
