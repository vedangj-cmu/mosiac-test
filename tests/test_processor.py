import pytest
from src.server.mcap_catalog import Catalog
from src.server.executors import McapReaderStage, H264ConvertorStage, AbstractStage
from src.server.processor import Processor, BufferPool
from src.server.models import Topic
from sensor_msgs import msg
from pathlib import Path


@pytest.fixture
def setup_data():
    current_file_path = Path(__file__)
    test_module_dir = current_file_path.parent
    mcap_file = (
        test_module_dir
        / "data/synthetic_images_1760323041/synthetic_images_1760323041_0.mcap"
    )

    data = {"mcap_file": str(mcap_file), "topic_name": "/mytopic/image/compressed"}
    yield data


def test_get_all_topic(setup_data):
    catalog = Catalog(setup_data["mcap_file"])
    topic_list = catalog.get_all_topics()
    assert len(topic_list) == 1
    assert type(topic_list[0]) is Topic


def test_get_duration(setup_data):
    catalog = Catalog(setup_data["mcap_file"])
    duration = catalog.get_duration()
    assert duration >= 10 * 1e9


def test_run_mcap_read_stage(setup_data):
    stage = McapReaderStage(setup_data["mcap_file"])
    topic = Topic(
        name=setup_data["topic_name"],
        schema_name="sensor_msgs/msg/CompressedImage",
        schema_type=msg.CompressedImage,
    )

    cnt = 0
    while (val := stage.next(topic)) is not None:
        data, ts = val
        cnt += 1
    assert cnt == 132


def test_get_execution_plan(setup_data):
    catalog = Catalog(setup_data["mcap_file"])
    catalog.set_include_topics([setup_data["topic_name"]])
    execution_plans = catalog.get_execution_plans()
    assert len(execution_plans) == 1
    assert all(
        [isinstance(i.executor_class, AbstractStage) for i in execution_plans[0].plan]
    )


def test_h264_convertor_stage(setup_data):
    reader_stage = McapReaderStage(setup_data["mcap_file"])
    stage = H264ConvertorStage(int(10954221312 + 1e9))
    stage.set_child_executor(reader_stage)

    topic = Topic(
        name=setup_data["topic_name"],
        schema_name="sensor_msgs/msg/CompressedImage",
        schema_type=msg.CompressedImage,
    )

    segment_cnt = 0
    while stage.next(topic) is not None:
        segment_cnt += 1
    assert segment_cnt == 6
    assert stage.get_total_messages_consumed() == 132


def test_processor_start(setup_data):
    buffer_pool = BufferPool()
    processor = Processor(
        setup_data["mcap_file"], buffer_pool, [setup_data["topic_name"]]
    )
    processor.start()

    assert buffer_pool.get_segment(setup_data["topic_name"], 2) is not None
    assert buffer_pool.get_segment(setup_data["topic_name"], 7) is None
