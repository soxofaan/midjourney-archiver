#!/usr/bin/env python
"""
Python command line tool to download Midjourney job metadata:
- text file with prompt used for each job
- JSON dump with full job metadata listing
"""

import collections

import datetime as dt
import itertools
import json
import logging
import os
import textwrap
from pathlib import Path
from typing import List, Optional, Union

import requests

_log = logging.getLogger("mj-metadata-archiver")


class MidjourneyMetadataArchiver:
    _text_wrapper = textwrap.TextWrapper(
        width=80,
        initial_indent=" " * 4,
        subsequent_indent=" " * 4,
        break_long_words=False,
        break_on_hyphens=False,
    )

    def __init__(self, archive_root: Path, user_id: str, session_token: str):
        self.archive_root = archive_root
        self.user_id = user_id
        self.session_token = session_token
        self.stats = collections.Counter()

    def request_recent_jobs(
        self,
        job_type: Union[str, None] = "upscale",
        from_date: Optional[dt.datetime] = None,
        page: Optional[int] = None,
        amount: int = 50,
    ) -> List[dict]:
        """
        Do `recent-jobs` request to midjourney API
        """
        url = "https://www.midjourney.com/api/app/recent-jobs/"
        params = {
            "amount": amount,
            "jobType": job_type,
            "orderBy": "new",
            "jobStatus": "completed",
            "userId": self.user_id,
            "dedupe": " true",
            "refreshApi": 0,
        }
        if from_date:
            params["fromDate"] = from_date
        if page:
            params["page"] = page
        headers = {
            "Cookie": f"__Secure-next-auth.session-token={self.session_token}",
        }

        _log.info(f"Requesting {url} with {params}")
        resp = requests.get(url=url, params=params, headers=headers)
        resp.raise_for_status()
        assert resp.headers["Content-Type"].startswith("application/json")
        job_listing = resp.json()
        if (
            isinstance(job_listing, list)
            and len(job_listing) > 0
            and isinstance(job_listing[0], dict)
        ):
            if all(f in job_listing[0] for f in ["id", "enqueue_time", "prompt"]):
                _log.info(f"Got job listing with {len(job_listing)} jobs")
                return job_listing
            if job_listing[0] == {"msg": "No jobs found."}:
                _log.info(f"Response: 'No jobs found'")
                return []
        raise ValueError(job_listing)

    def crawl(
        self,
        limit: Optional[int] = None,
        job_type: Union[str, None] = "upscale",
        from_date: Optional[str] = None,
    ):
        """
        Crawl the Midjourney API to collect job metadata
        """
        # TODO: option to get from_date from existing archive?
        # TODO: there seems to be a hard limit of 2500 items in total job listing
        pages = range(1, limit + 1) if limit else itertools.count(1)
        for page in pages:
            _log.info(f"Crawling for job info batch {page=}")
            job_listing = self.request_recent_jobs(
                from_date=from_date, page=page, job_type=job_type
            )
            if not job_listing:
                _log.info("Empty job listing batch: reached end of total job listing")
                break
            self.archive_job_listing(job_listing)
            # TODO: option to stop crawling if listing was already fully archived

            # Get "fromDate" for consistent paging in next requests.
            if from_date is None:
                from_date = job_listing[0]["enqueue_time"]

    def archive_job_listing(self, job_listing: List[dict]):
        for job_info in job_listing:
            self.archive_job_info(job_info)

    def archive_job_info(self, job_info: dict):
        job_id = job_info["id"]
        enqueue_time = job_info["enqueue_time"]
        _log.info(f"Archiving metadata of job {job_id} ({enqueue_time=})")

        self.stats["job"] += 1
        self.stats[f"job type={job_info['type']}"] += 1

        enqueue_time = dt.datetime.strptime(enqueue_time, "%Y-%m-%d %H:%M:%S.%f")
        job_dir = self.archive_root / enqueue_time.strftime("%Y/%Y-%m/%Y-%m-%d")
        job_dir.mkdir(parents=True, exist_ok=True)
        # Store raw metadata as JSON file
        # TODO: option to not/force overwriting existing metadata files?
        filename_base = f"{enqueue_time.strftime('%Y%m%d-%H%M%S')}_{job_id}"
        with (job_dir / f"{filename_base}.json").open("w") as f:
            # TODO: option to set indent/compactness?
            json.dump(job_info, f, indent=2)
        # Store prompt info as text file
        with (job_dir / f"{filename_base}.prompt.txt").open("w") as f:
            f.write("Prompt:\n")
            f.write(self._text_wrapper.fill(job_info["prompt"]) + "\n")
            f.write("\nFull command:\n")
            f.write(self._text_wrapper.fill(job_info["full_command"]) + "\n")


def main():
    logging.basicConfig(level=logging.INFO)

    # TODO: real CLI user interface
    archive_root = Path.cwd() / "mj-archive"
    user_id = os.environ.get("MIDJOURNEY_USER_ID") or input("user id:")
    session_token = os.environ.get("MIDJOURNEY_SESSION_TOKEN") or input(
        "session token:"
    )

    metadata_archiver = MidjourneyMetadataArchiver(
        archive_root=archive_root, user_id=user_id, session_token=session_token
    )
    try:
        metadata_archiver.crawl(
            limit=10,
            # limit=None,
            # job_type=None,
            job_type="upscale",
        )
    except KeyboardInterrupt:
        _log.info("Caught KeyboardInterrupt")

    _log.info(f"Crawling stats: {metadata_archiver.stats}")


if __name__ == "__main__":
    main()
