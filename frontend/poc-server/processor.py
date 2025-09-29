from mcap.reader import SeekingReader
from sensor_msgs.msg import CompressedImage
from rclpy.serialization import deserialize_message
import numpy as np
import cv2
import av
from av import VideoFrame
from fractions import Fraction
import sys


def decode_compressed_image(data: bytes) -> np.ndarray:
    nparr = np.frombuffer(data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def get_channel_name(channel_topic: str) -> str:
    return channel_topic.replace("/", "_").lstrip("_")


file_name = "sensor_data.mcap"
topic_timestamp_image_dict = {}
frame_rate = 30
per_frame_duration = int(1e9 / frame_rate)


with open(file_name, "rb") as f:
    mcap_reader = SeekingReader(f)
    mcap_stats = mcap_reader.get_summary().statistics

    mcap_start_time = mcap_stats.message_start_time
    mcap_end_time = mcap_stats.message_end_time
    total_frame = (mcap_end_time - mcap_start_time) // per_frame_duration + 1

    for schema, channel, message in mcap_reader.iter_messages(log_time_order=True):
        if (
            schema.name == "sensor_msgs/msg/CompressedImage"
            and sys.argv[1] in channel.topic
        ):  # Add the topic name as argv to process one by one
            timestamp_ns = message.log_time

            compressed_image: CompressedImage = deserialize_message(
                message.data, CompressedImage
            )
            image_data = decode_compressed_image(compressed_image.data)
            h, w = image_data.shape[:2]

            topic_name = get_channel_name(channel.topic)
            if topic_name not in topic_timestamp_image_dict:
                topic_timestamp_image_dict[topic_name] = {
                    "container": av.open(topic_name + ".mp4", "w")
                }
                s = topic_timestamp_image_dict[topic_name]["container"].add_stream(
                    "libx264", rate=frame_rate
                )
                s.width, s.height, s.pix_fmt, s.bit_rate = w, h, "yuv420p", 2_000_000
                topic_timestamp_image_dict[topic_name]["stream"] = s
                topic_timestamp_image_dict[topic_name]["pts"] = 0
                topic_timestamp_image_dict[topic_name]["last_img"] = None
                topic_timestamp_image_dict[topic_name]["next_ns"] = None

            # topic_timestamp_image_dict[get_channel_name(channel.topic)][timestamp_ns] = image_data # Memory heavy

            st = topic_timestamp_image_dict[topic_name]
            if st["next_ns"] is None:
                st["last_img"] = image_data
                st["next_ns"] = timestamp_ns
                continue

            while st["next_ns"] + per_frame_duration <= timestamp_ns:
                f = VideoFrame.from_ndarray(image_data, format="rgb24")
                f.pts, f.time_base = st["pts"], Fraction(1, frame_rate)
                st["pts"] += 1
                for pkt in st["stream"].encode(f):
                    st["container"].mux(pkt)
                st["next_ns"] += per_frame_duration

            st["last_img"] = image_data

    for t, st in topic_timestamp_image_dict.items():
        if st["next_ns"] is not None and st["last_img"] is not None:
            while st["next_ns"] + per_frame_duration <= mcap_end_time:
                f = VideoFrame.from_ndarray(st["last_img"], format="rgb24")
                f.pts, f.time_base = st["pts"], Fraction(1, frame_rate)
                st["pts"] += 1
                for pkt in st["stream"].encode(f):
                    st["container"].mux(pkt)
                st["next_ns"] += per_frame_duration

        for pkt in st["stream"].encode(None):
            st["container"].mux(pkt)
        st["container"].close()
