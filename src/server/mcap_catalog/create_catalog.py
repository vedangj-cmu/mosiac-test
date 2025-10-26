from pathlib import Path
from typing import List, Type, Any
from sensor_msgs import msg
from src.server.executors import (
    AbstractStage,
    H264ConvertorStage,
    McapReaderStage,
    SegmentNode,
)
from src.server.models import Topic
from src.repository.rosbag import BagReader


class ExecutionNode:
    def __init__(
        self,
        executor_class: AbstractStage,
        child_executor_class: AbstractStage | None = None,
    ) -> None:
        self.executor_class = executor_class
        self.child_executor_class = child_executor_class


class ExecutionPlan:
    """An execution plan is a list of executors
    that are called sequentially, all executors are initialized here.

    Example: To process a topic that the schema_type CompressedImage, the execution plan would
    look like = [ExecutionNode(H264ConvertorStage, next=McapReaderStage), ExecutionNode(McapReaderStage, next=None)]
    """

    def __init__(self, topic: Topic) -> None:
        self.topic = topic
        self.plan: List[ExecutionNode] = []

    def add_stage(self, execution_node: ExecutionNode) -> None:
        execution_node.executor_class.set_child_executor(
            execution_node.child_executor_class
        )
        self.plan.append(execution_node)

    def next(self) -> SegmentNode | None:
        if len(self.plan) == 0:
            return None
        return self.plan[0].executor_class.next(self.topic)


class Catalog:
    """This class reads and stores the metadata for a mcap file. This metadata is used to
    generate execution plan based on the schema type. Read about #ExecutionPlan.

    All the mapping between strings of schema_types and their class objects is done in this
    class.

    Finally, there are 3 things that this class exposes
        get_all_topics() : List of all topics as List[Topic]
        get_duration() : Duration of the mcap
        set_include_topics(List[str]) : Takes in list of topics to be included.
        get_execution_plans() : Execution plan of topics set as included, defaults to all topics.
    """

    def __init__(self, filename) -> None:
        self._filename = filename
        self._topics: List[Topic] = []
        self._execution_plans: List[ExecutionPlan] = []
        self._included_topics: List[str] = []
        self._duration = 0

    def _get_type_from_schema_type_str(self, schema_type: str) -> Type[Any] | None:
        values = {
            "sensor_msgs/msg/CameraInfo": msg.CameraInfo,
            "sensor_msgs/msg/CompressedImage": msg.CompressedImage,
            "sensor_msgs/msg/PointCloud2": msg.PointCloud2,
        }
        return values.get(schema_type)

    def _get_topics_and_duration_from_mcap(self):
        bag_reader = BagReader(Path(self._filename))
        bag_reader.__enter__()

        topic_types = bag_reader._reader.get_all_topics_and_types()
        metadata = bag_reader._reader.get_metadata()
        self._duration = metadata.duration.nanoseconds

        # NOTICE: A buffer is added to the duration
        # as we generate videos, and round of the frames timestamps to their
        # nearest multiple of 1/fps seconds. Ex - 1/30. There is a possible
        # error of 1/60. It is okay to copy a few frames at the end that to
        # miss a valid frame. Thus a buffer is added here for error correction.
        self._duration += 1e9

        for topic_metadata in topic_types:
            self._topics.append(
                Topic(
                    name=topic_metadata.name,
                    schema_name=topic_metadata.name,
                    schema_type=self._get_type_from_schema_type_str(
                        topic_metadata.type
                    ),
                )
            )

    def get_all_topics(self) -> List[Topic]:
        if len(self._topics) == 0:
            self._get_topics_and_duration_from_mcap()
        return self._topics

    def get_duration(self) -> int:
        if len(self._topics) == 0:
            self._get_topics_and_duration_from_mcap()
        return self._duration

    def set_include_topics(self, topic_list: List[str]):
        self._included_topics = topic_list

    def _populate_execution_plan(self):
        if len(self._topics) == 0:
            self._get_topics_and_duration_from_mcap()

        for topic in self._topics:
            if (
                len(self._included_topics) > 0
                and topic.name not in self._included_topics
            ):
                continue

            if topic.schema_type is None:
                continue

            execution_plan = ExecutionPlan(topic)

            reader_stage = McapReaderStage(self._filename)
            if topic.schema_type is msg.CompressedImage:
                execution_plan.add_stage(
                    ExecutionNode(H264ConvertorStage(self._duration), reader_stage)
                )
                execution_plan.add_stage(ExecutionNode(reader_stage, None))
            elif topic.schema_type is msg.PointCloud2:
                pass
            self._execution_plans.append(execution_plan)

    def get_execution_plans(self):
        if len(self._execution_plans) == 0:
            self._populate_execution_plan()
        return self._execution_plans
