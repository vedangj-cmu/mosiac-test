import open3d as o3d
import numpy as np
from mcap.reader import SeekingReader
from rclpy.serialization import deserialize_message
import sensor_msgs_py.point_cloud2 as pc2
from sensor_msgs.msg import PointCloud2
import time


vis = o3d.visualization.Visualizer()
render_opt = vis.get_render_option()
render_opt.point_size = 2.0
render_opt.background_color = np.asarray([0.1, 0.1, 0.1])
pcd = o3d.geometry.PointCloud()


file_name = "sensor_data.mcap"
with open(file_name, "rb") as f:
    mcap_reader = SeekingReader(f)

    is_first_frame = True

    for schema, channel, message in mcap_reader.iter_messages(
        topics=["/sensing/lidar/front/pointcloud_raw_ex"], log_time_order=True
    ):
        cloud: PointCloud2 = deserialize_message(message.data, PointCloud2)
        point_xyz = pc2.read_points(cloud, field_names=["x", "y", "z"], skip_nans=True)
        points = [list(t) for t in point_xyz]

        if len(points) == 0:
            print("Skipping empty frame.")
            continue

        pcd.points = o3d.utility.Vector3dVector(points)
        pcd.paint_uniform_color([0.2, 0.8, 0.2])

        if is_first_frame:
            vis.add_geometry(pcd)
            vis.reset_view_point(True)
            is_first_frame = False
        else:
            vis.update_geometry(pcd)
        vis.update_renderer()
        time.sleep(0.1)

vis.destroy_window()
