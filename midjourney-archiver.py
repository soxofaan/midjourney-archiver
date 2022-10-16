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

_log = logging.getLogger("midjourney-archiver")


class MetadataArchiver:
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

    def request_recent_jobs(
        self,
        job_type: Union[str, None] = "upscale",
        from_date: Optional[dt.datetime] = None,
        page: Optional[int] = None,
        amount: int = 50,
    ) -> List[dict]:
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
        if isinstance(job_listing, list):
            if len(job_listing) > 0:
                if isinstance(job_listing[0], dict):
                    if all(
                        f in job_listing[0] for f in ["id", "enqueue_time", "prompt"]
                    ):
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
        from_date: Optional[str] = None
    ):
        # TODO: option to get from_date from existing archive?
        # TODO: there seems to be a hard limit of 2500 items in total job listing
        pages = range(1, limit + 1) if limit else itertools.count(1)
        stats = collections.Counter()
        for page in pages:
            _log.info(f"Crawling for job info batch {page=}")
            job_listing = self.request_recent_jobs(
                from_date=from_date, page=page, job_type=job_type
            )
            if not job_listing:
                _log.info("Empty job listing batch: reached end of total job listing")
                break
            self.archive_job_listing(job_listing, stats=stats)
            # TODO: option to stop crawling if listing was already fully archived

            # Get "fromDate" for consistent paging in next requests.
            if from_date is None:
                from_date = job_listing[0]["enqueue_time"]
        _log.info(f"Finished crawling: {stats=}")

    def archive_job_listing(
        self, job_listing: List[dict], stats: Optional[dict] = None
    ):
        for job_info in job_listing:
            self.archive_job_info(job_info, stats=stats)

    def archive_job_info(self, job_info: dict, stats: Optional[dict] = None):
        job_id = job_info["id"]
        enqueue_time = job_info["enqueue_time"]
        _log.info(f"Archiving metadata of job {job_id} ({enqueue_time=})")

        if stats is not None:
            stats["job"] += 1
            stats[f"job type={job_info['type']}"] += 1

        date = dt.datetime.strptime(enqueue_time.split(" ")[0], "%Y-%m-%d").date()
        job_dir = self.archive_root / date.strftime("%Y/%Y-%m/%Y-%m-%d")
        job_dir.mkdir(parents=True, exist_ok=True)
        # Store raw metadata as JSON file
        # TODO: option to not/force overwriting existing metadata files?
        with (job_dir / f"{job_id}.json").open("w") as f:
            json.dump(job_info, f, indent=2)
        # Store prompt info as text file
        with (job_dir / f"{job_id}.prompt.txt").open("w") as f:
            f.write("Prompt:\n")
            f.write(self._text_wrapper.fill(job_info["prompt"]) + "\n")
            f.write("\nFull command:\n")
            f.write(self._text_wrapper.fill(job_info["full_command"]) + "\n")


def main():
    logging.basicConfig(level=logging.INFO)

    # TODO: real CLI user interface
    download_dir = Path.cwd() / "jobs"
    user_id = os.environ.get("MIDJOURNEY_USER_ID") or input("user id:")
    session_token = os.environ.get("MIDJOURNEY_SESSION_TOKEN") or input("session token:")

    metadata_archiver = MetadataArchiver(
        archive_root=download_dir, user_id=user_id, session_token=session_token
    )

    metadata_archiver.crawl(
        limit=5,
        # limit=None,
        job_type=None,
    )
    return True


if __name__ == "__main__":
    main()
