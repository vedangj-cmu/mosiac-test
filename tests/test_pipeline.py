from pathlib import Path
from rosbag2_py import StorageOptions, ConverterOptions, SequentialWriter, TopicMetadata
from rclpy.serialization import serialize_message
from sensor_msgs.msg import CompressedImage, CameraInfo
from typing import List
import shutil
from collections import Counter
from pyfakefs.fake_filesystem_unittest import TestCase
from PIL import Image

from src.repository.repository import Repository, MosaicRepoException
from src.pipeline.extract import scan_and_extract_all, _extract_images_from_bag


class PipelineTestCase(TestCase):

    testdir = Path().cwd() / "testdir"

    def setUp(self):
        self.testdir.mkdir()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.testdir)

    @staticmethod
    def create_rosbag(path: Path, topics: List[str], length: int):
        writer = SequentialWriter()
        writer.open(
            StorageOptions(uri=path.as_posix(), storage_id="mcap"),
            ConverterOptions(
                input_serialization_format="cdr", output_serialization_format="cdr"
            ),
        )

        for topic in topics:
            writer.create_topic(
                TopicMetadata(
                    id=0,
                    name=topic,
                    type="sensor_msgs/msg/CompressedImage",
                    serialization_format="cdr",
                )
            )

        # We might also come across camera info topics
        writer.create_topic(
            TopicMetadata(
                id=0,
                name="/passenger_front/camera_info",
                type="sensor_msgs/msg/CameraInfo",
                serialization_format="cdr",
            )
        )

        # Make sure we can handle topics and types we don't know
        writer.create_topic(
            TopicMetadata(
                id=0,
                name="/foo/bar/baz",
                type="garbage_msgs/msg/Unknown",
                serialization_format="cdr",
            )
        )

        fake_img = Image.new("RGB", (10, 10)).tobytes()
        start_time = 0
        for i in range(length):
            msg = CompressedImage()
            # JPEG image
            msg.data = fake_img
            timestamp = start_time + (i * 2000)
            writer.write(topics[i % len(topics)], serialize_message(msg), timestamp)

            if i % 10 == 0:
                # Add a camera info message every 10 frames just for fun
                cam_info = CameraInfo()
                writer.write(
                    "/passenger_front/camera_info",
                    serialize_message(cam_info),
                    timestamp + 1,
                )

        writer.write(
            "/foo/bar/baz",
            b"randombytes",
            timestamp + 54321,
        )

    def test_single_bag_extract(self):
        repo = Repository(cwd=self.testdir, create=True)

        bag_path = self.testdir / "foo"

        num_images_per_camera = 64
        self.create_rosbag(
            path=bag_path,
            topics=[
                "/center_front/image_rect/compressed",
                "/passenger_front/image_rect/compressed",
                "/center_rear/image_rect/compressed",
                "/passenger_rear/image_rect/compressedDepth",
            ],
            length=num_images_per_camera * 4,
        )

        scan_and_extract_all(repo=repo)

        # Check that we have the right number of images
        # by reading the output directory
        counts = Counter()
        image_dir = bag_path / "images"
        for p in image_dir.iterdir():
            if p.suffix == ".jpeg":
                camera = p.stem.split("_")[2]
                counts[camera] += 1

        assert image_dir.exists()
        assert counts["frontcenter"] == num_images_per_camera
        assert counts["frontpassenger"] == num_images_per_camera
        assert counts["rearcenter"] == num_images_per_camera
        assert counts["rearpassenger"] == num_images_per_camera

        # Check that we cannot overwrite an existing directory
        self.assertRaises(
            MosaicRepoException,
            _extract_images_from_bag,
            repo=repo,
            bag_path=bag_path,
            output_dir=image_dir,
        )
