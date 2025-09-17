from typing import Self, Literal
from pydoc import locate
import os
from PIL import Image, ImageDraw, ImageFont, ImageFile
import io
from datetime import datetime

from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import CompressedImage, CameraInfo


class BagReader:
    """
    A simple class for reading rosbags and iterating through them

    Example Usage
    ```python
    with BagReader(uri="foo/bar/baz") as bag:
       bag.print_metadata()
       for topic, data, timestamp in list(bag):
           print(topic)
    ```
    """

    def __init__(self, uri: str, storage_id: Literal["mcap", "sqlite3"] = "mcap"):
        self._reader = SequentialReader()
        self._storage_options = StorageOptions(uri=uri, storage_id=storage_id)
        self._converter_options = ConverterOptions("", "")

    def __enter__(self) -> Self:
        self._reader.open(self._storage_options, self._converter_options)

        # This hack allows us to use the topic name to import the needed class
        # See: https://github.com/ros2/rosbag2/issues/1692
        # FIXME: This will require better error handling

        # Map types (strings of the form ex. "sensor_msgs/msg/CompressedImage")
        # to associated python type ex. sensor_msgs.msg.CompressedImage
        type_to_def = {
            definition.topic_type: locate(definition.topic_type.replace("/", "."))
            for definition in self._reader.get_all_message_definitions()
        }

        # Map the topics (string, ex. /driver_rear/image_rect/compressed) in this bag to their python classes
        self._topic_to_def = {
            meta_info.name: type_to_def[meta_info.type]
            for meta_info in self._reader.get_all_topics_and_types()
        }
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._reader:
            self._reader.close()
        if exc_type:
            print(f"An exception occurred: {exc_val}")
            return False  # Re-raise the exception

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> tuple[str, object, datetime]:
        if self._reader.has_next():
            msg = self._reader.read_next()
            assert len(msg) == 3  # There is a topic, data and timestamp
            topic, serial_data, timestamp = msg

            # Deserialize using the python class (automatically imported) associated
            # with that topic
            data = deserialize_message(serial_data, self._topic_to_def[topic])
            dt_object = datetime.fromtimestamp(timestamp / 1_000_000_000)

            return topic, data, dt_object
        else:
            raise StopIteration

    def print_metadata(self):
        print(self._reader.get_metadata())


def annotate_img(img: ImageFile, text: str):
    """
    A utility function to add text to a Pillow image

    TODO: Remove me, this is temporary for visualization purposes locally only
    """
    split_text = text.split("\n")
    longest_line = split_text[split_text.index(max(split_text, key=lambda s: len(s)))]

    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=100)
    # Place it at the top right corner
    draw.text(
        (
            img.width
            - draw.textlength(
                longest_line,
                font=font,
            )  # Don't fall off the image
            - 20,  # A little offset
            50,  # A little offset
        ),
        text,
        fill=(255, 255, 0),
        font=font,
    )


def ingest(bag_path: str, img_path: str):
    """
    A WIP

    Given a path to a rosbag, output all the images as a single flat
    output directory as specified by img_path
    """
    # Make the output dir (and associated structure) if needed
    os.makedirs(img_path, exist_ok=True)

    with BagReader(uri=bag_path) as bag:
        bag.print_metadata()
        # FIXME: NOTE WELL, this is restricted to 20 for now
        # since dumping all the images is a little bit unneeded right now
        # of course this will be removed at a later date
        for topic, data, timestamp in list(bag)[:200]:
            match data:
                case CameraInfo():
                    # https://docs.ros2.org/latest/api/sensor_msgs/msg/CameraInfo.html
                    print(
                        f"{timestamp}\t{topic}\t{data.header.frame_id=}, {data.height=}, {data.width=},"
                    )
                case CompressedImage():
                    # https://docs.ros2.org/latest/api/sensor_msgs/msg/CompressedImage.html
                    img_buf = io.BytesIO(data.data)
                    img = Image.open(img_buf)
                    print(
                        f"{timestamp}\t{topic}\t Saving [fmt={img.format}, size={img.size}]"
                    )
                    camera_name = topic.split("/")[1]
                    annotate_img(
                        img, f"{camera_name}\n{timestamp.strftime('%H:%M:%S.%f')}"
                    )
                    img.save(
                        f"{img_path}/{camera_name}_{timestamp.strftime('%Y_%m_%d_%H_%M_%S_%f')}.jpeg"
                    )
                    img.close()
                case _:
                    print(f"Unknown message type: {type(data)}")
