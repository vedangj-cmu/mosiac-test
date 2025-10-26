from typing import Dict, Deque, List
from collections import deque
from src.server.mcap_catalog import Catalog
from src.server.executors import SegmentNode


class BufferPool:
    """Represent a buffer pool.

    This class has a topic wise queue, a process would enqueue segments / chunks
    and another process would consume them. Later a LRU Cache can also be
    implemented.
    """

    def __init__(self) -> None:
        self.topics: Dict[str, Deque[SegmentNode]] = {}

    def add_segment(self, topic_name: str, segment: SegmentNode):
        """Add a segment on a topic. All the last executors must return a
        SegmentNode

        Args:
            topic_name (str): Topic name
            segment (SegmentNode): A SegmentNode(data: bytes) object
        """
        if topic_name not in self.topics:
            self.topics[topic_name] = deque()
        self.topics[topic_name].append(segment)

    def get_segment(self, topic_name: str, segment_idx: int) -> SegmentNode | None:
        """Get a particular segment for a topic. None if topic not available or
        segment_idx out of bound

        Args:
            topic_name (str): Topic name
            segment_idx (int): Index of the segment

        Returns:
            SegmentNode | None: SegmentNode or none if not available
        """
        if topic_name not in self.topics:
            return None

        if segment_idx >= len(self.topics[topic_name]):
            return None

        return self.topics[topic_name][segment_idx]


class Processor:
    """This class is responsible for populating the buffer pool.
    It maintains a list of execution plans, returned to it by the McapCatalog,
    keeps on calling the next until no more data is available on any topic
    """

    def __init__(
        self,
        filename: str,
        buffer_pool: BufferPool = BufferPool(),
        include_topics: List[str] = [],
    ) -> None:
        self._filename = filename
        self._buffer_pool = buffer_pool  # dependency injection

        catalog = Catalog(self._filename)
        catalog.set_include_topics(include_topics)
        self._execution_plans = catalog.get_execution_plans()

    def start(self):
        total_plan_cnt = len(self._execution_plans)
        plan_processed = set()

        idx = 0
        while True:
            curr_plan = self._execution_plans[idx % total_plan_cnt]
            idx += 1

            next_segment = curr_plan.next()
            if next_segment is None:
                plan_processed.add(curr_plan.topic.name)
                if len(plan_processed) == total_plan_cnt:
                    break  # all topics processed
                continue

            self._buffer_pool.add_segment(curr_plan.topic.name, next_segment)
