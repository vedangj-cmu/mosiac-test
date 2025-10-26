import av
import io
import numpy as np
import cv2
import math
from abc import ABC, abstractmethod
from pathlib import Path
from av import VideoFrame
from typing import Dict, Deque, Tuple
from collections import deque
from src.server.models import Topic
from src.repository.rosbag import BagReader
from sensor_msgs import msg


class SegmentNode:
    """A single node of data that is stored in
    the buffer pool. The `data` here is bytes, so it could
    be an video or a lidar etc.
    """

    def __init__(self, data: bytes):
        self.data = data


class AbstractStage(ABC):

    def __init__(self) -> None:
        self.child_executor: AbstractStage | None = None

    def set_child_executor(self, child_executor):
        self.child_executor = child_executor

    @abstractmethod
    def next(self, topic: Topic):
        pass


class McapReaderStage(AbstractStage):
    """Class responsible for reading the MCAP files sequentially

    Methods:
        next(topic) -> Next message on this topic
    """

    def __init__(self, filename: str) -> None:
        super().__init__()
        self._filename = filename
        self._topic_wise_queue: Dict[str, Deque] = {}
        self._bag_reader: BagReader = BagReader(uri=Path(filename))
        self._bag_reader.__enter__()
        self._iterator = iter(self._bag_reader)

    def next(self, topic: Topic) -> Tuple[object, int] | None:
        if topic.name not in self._topic_wise_queue:
            self._topic_wise_queue[topic.name] = deque()

        if (
            self._topic_wise_queue[topic.name]
            and len(self._topic_wise_queue[topic.name]) > 0
        ):
            return self._topic_wise_queue[topic.name].popleft()

        # Read till we reach the next message of the topic we
        # need. Add all messages for all other topics to queue
        # so that we don't waste IO.

        # TODO: Check if this always returns sorted messages
        # just in case they are not
        try:
            while True:
                topic_from_file, data, dt_object = next(self._iterator)
                # Convert datetime back to nanosecond timestamp
                ts = int(dt_object.timestamp() * 1_000_000_000)

                if topic_from_file == topic.name:
                    return (data, ts)
                else:
                    if topic_from_file not in self._topic_wise_queue:
                        self._topic_wise_queue[topic_from_file] = deque()
                    self._topic_wise_queue[topic_from_file].append((data, ts))
        except StopIteration:
            return None


class H264ConvertorStage(AbstractStage):
    """Class to create chucks of video to be streamed to the UI

    Methods:
        next(topic) -> Next chuck stored as a SegmentNode

    Summary:
        The segment size is set as 2 and the fps is set as 30. This class
        would request for the next message from its child executor which always
        would be a McapReaderStage. Once it has enough messages to create a video
        of segment_size, it use pyav to make the video and store is as a IOBuffer
        which is enclosed in a SegmentNode Object.

        Each SegmentNode is a mpegts segment. That can be played on a browser.
        mpegts is the default video format used by HLS. HLS also requires a index file
        that is used as a playlist, in our case the bufferPool can be used as a playlist,
        the frontend can request for the segment is needs.
    """

    def __init__(self, duration: int) -> None:
        super().__init__()
        self._duration = duration
        self.segment_size = 2
        self.fps = 30
        self.bitrate = 2_000_000
        self.per_frame_duration = int(1e9 / self.fps)
        self.segment_duration_ns = self.segment_size * int(1e9)
        self._is_initialized: bool = False

        # Start ts of the first segment
        self._recording_start_ns: int = 0
        self._last_frame: np.ndarray | None = None
        self._buffered_val: tuple | None = None
        self._current_global_frame_index: int = 0

        # Cnt for debugging and Test cases
        self._total_messages_consumed: int = 0

    def _decode_compressed_image(
        self, compressed_image: msg.CompressedImage
    ) -> np.ndarray:
        np_arr = np.frombuffer(compressed_image.data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def get_total_messages_consumed(self) -> int:
        return self._total_messages_consumed

    def next(self, topic: Topic) -> SegmentNode | None:
        """Returns the next segment as a 2 sec video

        Summary:
            For each segment we start by calculating the number of frame required,
            i.e fps * duration of this segment. Then we request the McapReader for
            new messages. Each messages comes with its timestamp, we round that
            to find the closest appropriate where can be place this frame.

            Finally, we fill the missing frames in middle with the value of the previous
            known frame.

            A video is then generated.
        """

        assert self.child_executor is not None

        if not self._is_initialized:
            val = (
                self._buffered_val
                if self._buffered_val
                else self.child_executor.next(topic)
            )

            # This is an empty mcap topic as _is_initialized = false and val = None
            if val is None:
                return None

            assert len(val) == 2
            data, ts = val
            self._recording_start_ns = ts
            self._last_frame = self._decode_compressed_image(data)
            h, w = self._last_frame.shape[:2]

            self._buffered_val = val
            self._is_initialized = True

        recording_end_ns = self._recording_start_ns + self._duration
        segment_start_ns = self._recording_start_ns + (
            self._current_global_frame_index * self.per_frame_duration
        )

        # Our current start idx is more than total length of video
        if segment_start_ns >= recording_end_ns:
            return None

        segment_end_ns = min(
            segment_start_ns + self.segment_duration_ns, recording_end_ns
        )
        frames_to_generate = math.ceil(
            (segment_end_ns - segment_start_ns) / self.per_frame_duration
        )
        if frames_to_generate <= 0:
            return None  # never reach

        frame_map: Dict[int, np.ndarray] = {}
        while self._buffered_val is not None:
            data, ts = self._buffered_val

            # This would be a part of next segment, so buffer is now but don't use
            # it in this segment
            if ts >= segment_end_ns:
                break

            time_offset = ts - self._recording_start_ns

            # Find the perfect index based on message's ts
            index = round(time_offset / self.per_frame_duration)

            self._total_messages_consumed += 1
            frame_map[int(index)] = self._decode_compressed_image(data)
            self._buffered_val = self.child_executor.next(topic)

        # Fill a black frame till we get the first message of the first segment
        if self._last_frame is None:
            self._last_frame = np.zeros((h, w, 3), dtype=np.uint8)

        h, w = self._last_frame.shape[:2]

        output_buffer = io.BytesIO()
        container = av.open(file=output_buffer, mode="w", format="mpegts")
        stream = container.add_stream("libx264", rate=self.fps)
        stream.width, stream.height, stream.pix_fmt, stream.bit_rate = (
            w,
            h,
            "yuv420p",
            self.bitrate,
        )

        # A pts is "Presentation time" which is a multiple of 1/fps.
        # Basically, its pyav's way of saying frame_index
        for pts in range(frames_to_generate):
            global_index = self._current_global_frame_index + pts
            frame_to_encode = frame_map.get(global_index)

            # Either get the new frame, or fill in the last known
            if frame_to_encode is not None:
                self._last_frame = frame_to_encode
            else:
                frame_to_encode = self._last_frame

            pyav_frame = VideoFrame.from_ndarray(frame_to_encode, format="rgb24")
            pyav_frame.pts = pts
            for packet in stream.encode(pyav_frame):
                container.mux(packet)

        self._current_global_frame_index += frames_to_generate
        for packet in stream.encode(None):
            container.mux(packet)
        container.close()
        return SegmentNode(data=output_buffer.getvalue())


class CompressionStage(AbstractStage):
    def __init__(self) -> None:
        super().__init__()

    def next(self, topic: Topic) -> SegmentNode | None:
        return None
