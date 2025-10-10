from pathlib import Path
from src.repository.rosbag import BagReader
from src.repository.repository import Repository, MosaicRepoException

import logging
import sys

logger = logging.getLogger(__name__)


def scan_and_extract_all(repo: Repository):
    """Scan the repository for new logs and extract images for each new log."""
    logger.info(
        "Scanning repository for new logs: %s", getattr(repo, "root_path", "<unknown>")
    )
    repo.update_state()

    new_logs = repo.get_new_logs()
    logger.info("Found %d new log(s) to process", len(new_logs))

    for log in new_logs:
        log_path = Path(log.log_path)
        image_path = log_path.parent / "images"
        logger.debug("Preparing to extract images from %s to %s", log_path, image_path)
        _extract_images_from_bag(repo=repo, bag_path=log_path, output_dir=image_path)


def _extract_images_from_bag(repo: Repository, bag_path: Path, output_dir: Path):
    """
    Given a path to a rosbag, extract all images and store them in the given
    output directory.
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        logger.exception("Output directory already exists: %s", output_dir)
        raise MosaicRepoException(
            f"Cannot extract images to existing directory {output_dir}"
        )

    saved = 0
    with BagReader(uri=bag_path) as bag:
        for topic, data, timestamp in bag:
            file_name = image_path_from_message(topic, timestamp)

            img_file = output_dir / file_name
            img_file.touch()
            img_file.write_bytes(data.data)
            saved += 1

    logger.info("Extraction complete for %s: %d image(s) saved", bag_path, saved)

    repo.add_images(log_path=bag_path, img_dir_path=output_dir)
    logger.info("Registered images with repository for %s -> %s", bag_path, output_dir)


def image_path_from_message(topic: str, timestamp) -> str:
    """Given a ROS topic and timestamp, return the expected image path."""
    # Format the filename as <timestamp>_camera_<camera_name>.jpeg
    time = timestamp.strftime("%Y%m%d%H%M%S%f")
    camera = "".join(topic.split("/")[1].split("_")[::-1])
    file_name = f"{time}_camera_{camera}.jpeg"
    return file_name


# FIXME: to remove once the cli is done
if __name__ == "__main__":  # pragma: no cover
    repo_path = Path(sys.argv[1])
    repo = Repository(cwd=repo_path, create=True)
    scan_and_extract_all(repo=repo)
