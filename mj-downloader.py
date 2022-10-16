#!/usr/bin/env python
"""
Python command line tool to download images linked from
Midjourney metadata archive
"""
import collections
import json
import logging
from pathlib import Path

import requests

_log = logging.getLogger("mj-metadata-archiver")


class MidjourneyDownloader:
    def __init__(self):
        self.stats = collections.Counter()

    def walk_archive(self, archive_root: Path):
        for job_info_path in archive_root.glob("**/*.json"):
            _log.info(f"Processing {job_info_path}")
            self.download_from_metadata_file(job_info_path)

    def download_from_metadata_file(self, job_info_path: Path):
        # TODO: try-except for json.loads
        job_info = json.loads(job_info_path.read_text(encoding="utf8"))

        if all(f in job_info for f in ["id", "type", "image_paths"]):
            job_type = job_info["type"]
            # TODO: option to decide which types/jobs to download?
            if job_type == "upscale":
                image_paths = job_info["image_paths"]
                for i, image_url in enumerate(job_info["image_paths"]):
                    extension = image_url.split(".")[-1].lower()
                    if extension not in ["png", "jpg", "jpeg"]:
                        raise ValueError(extension)
                    image_index = "" if len(image_paths) == 1 else f"-{i + 1}"
                    download_path = (
                        job_info_path.parent
                        / f"{job_info_path.stem}{image_index}.{extension}"
                    )
                    if download_path.exists():
                        _log.info(f"Skipping, already exists: {download_path}")
                        self.stats["skip already downloaded"] += 1
                    else:
                        self.download_url(image_url, download_path)
                        self.stats["download"] += 1
        else:
            _log.warning(f"Skipping invalid metadata file {job_info_path}")
            self.stats["skip invalid metadata"] += 1

    def download_url(self, url: str, path: Path):
        _log.info(f"Downloading {path} from {url}")
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with path.open("wb") as f:
                for chunk in response.iter_content(chunk_size=None):
                    f.write(chunk)
        return path


def main():
    logging.basicConfig(level=logging.INFO)

    # TODO: real CLI user interface
    archive_root = Path.cwd() / "mj-archive"

    downloader = MidjourneyDownloader()
    try:
        downloader.walk_archive(archive_root=archive_root)
    except KeyboardInterrupt:
        _log.info("Caught KeyboardInterrupt")
    _log.info(f"Download stats: {downloader.stats}")


if __name__ == "__main__":
    main()
