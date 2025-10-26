from typing import Self
from datetime import datetime
from pathlib import Path
import logging

from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import CompressedImage, CameraInfo

SUPPORTED_MSGS = {
    "sensor_msgs/msg/CompressedImage": CompressedImage,
    "sensor_msgs/msg/CameraInfo": CameraInfo,
}


class BagReader:
    """
    A simple class for reading rosbags and iterating through them

    Example Usage
    ```python
    with BagReader(uri="foo/bar/baz") as bag:
       bag.print_metadata()
       for topic, data, timestamp in bag:
           print(topic)
    ```
    """

    # The only currently supported storage id
    STORAGE_ID = "mcap"

    def __init__(self, uri: Path):
        # module logger
        self._logger = logging.getLogger(__name__)

        self._reader = SequentialReader()
        # stash the uri string for clearer logs
        self._uri = uri.as_posix()
        self._storage_options = StorageOptions(
            uri=self._uri, storage_id=self.STORAGE_ID
        )
        self._converter_options = ConverterOptions("", "")

    def __enter__(self) -> Self:
        self._logger.debug("Opening bag at %s", self._uri)
        self._reader.open(self._storage_options, self._converter_options)

        # This hack allows us to use the topic name to import the needed class
        # See: https://github.com/ros2/rosbag2/issues/1692
        # FIXME: This will require better error handling

        # Map types (strings of the form ex. "sensor_msgs/msg/CompressedImage")
        # to associated python type ex. sensor_msgs.msg.CompressedImage
        # TODO: add error handling for unsupported types
        type_to_def = {}
        topic_types = self._reader.get_all_topics_and_types()
        for topic_metadata in topic_types:
            typ = SUPPORTED_MSGS.get(topic_metadata.type, None)
            if typ is None:
                self._logger.error(
                    "Unsupported message type in bag %s: %s",
                    self._uri,
                    topic_metadata.type,
                )
            type_to_def[topic_metadata.type] = typ

        # Map the topics (string, ex. /driver_rear/image_rect/compressed) in this bag to their python classes
        self._topic_to_def = {
            meta_info.name: type_to_def[meta_info.type]
            for meta_info in self._reader.get_all_topics_and_types()
        }
        self._logger.debug("Discovered topics: %s", list(self._topic_to_def.keys()))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._reader:
            self._reader.close()
        if exc_type:
            # Log the exception with stacktrace
            self._logger.exception(
                "Exception while reading bag %s: %s",
                getattr(self, "_uri", "<unknown>"),
                exc_val,
            )
            return False  # Re-raise the exception

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> tuple[str, object, datetime]:
        if self._reader.has_next():
            msg = self._reader.read_next()
            assert len(msg) == 3  # There is a topic, data and timestamp
            topic, serial_data, timestamp = msg
            # We should have a mapping for this topic
            assert topic in self._topic_to_def

            # Deserialize using the python class (automatically imported) associated
            # with that topic
            data = None
            try:
                typ = self._topic_to_def[topic]
                if typ is None:
                    self._logger.debug(
                        "Skipping message on unsupported topic %s", topic
                    )
                    return self.__next__()

                if typ != CompressedImage:
                    # TODO: LiDAR data will eventually be supported
                    self._logger.debug(
                        "Skipping non-compressed image message on topic %s (type=%s)",
                        topic,
                        typ,
                    )
                    return self.__next__()

                data = deserialize_message(serial_data, typ)
            except Exception as exc:
                # If we can't deserialize, log at debug and skip this message
                # Deserialization failures may be common if message types don't match
                self._logger.debug(
                    "Failed to deserialize message on topic %s: %s",
                    topic,
                    exc,
                    exc_info=True,
                )
                return self.__next__()

            dt_object = datetime.fromtimestamp(timestamp / 1_000_000_000)
            self._logger.debug(
                "Yielding CompressedImage from %s at %s", topic, dt_object.isoformat()
            )
            return topic, data, dt_object
        else:
            raise StopIteration

    def print_metadata(self) -> None:  # pragma: no cover
        """Print the metadata for this bag"""
        print(self._reader.get_metadata())
