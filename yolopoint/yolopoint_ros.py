#!/usr/bin/env python3
import os
import cv2
import yaml
import numpy as np
from glob import glob

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

from object_instance_msgs.msg import ObjectInstance2D, ObjectInstance2DArray
from keypoint_msg.msg import KeypointArray
from demo import YoloPointFrontend

import ament_index_python.packages


class YoloCfg:
    """Configuration loader replacing ROS1 params."""

    def __init__(self, node: Node):
        pkg_path = ament_index_python.packages.get_package_share_directory('yolopoint')

        # Load parameters from ROS2 params or use defaults
        config_file = node.get_parameter_or('config', os.path.join('configs', 'campus_inference.yaml'))
        self.config_path = os.path.join(pkg_path, config_file)
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        weights_file = node.get_parameter_or('weights_path', 'weights/CampusKitti/checkpoints/CampusKitti_46_2291_ckpt.pth.tar')
        self.weights_path = os.path.join(pkg_path, weights_file)

        self.filter_pts = node.get_parameter_or('filter_pts', True)
        self.visualize = node.get_parameter_or('visualize', False)
        self.camera_name = node.get_parameter_or('sensor_name', 'surround/front')

        self.publish = True
        self.display_scale = 0.25
        self.source_type = 'ros'
        self.source = f'/sensor/camera/{self.camera_name}/image_rect_color'

        self.template_paths = self.config.get('templates', {})
        for t in self.template_paths:
            self.template_paths[t] = os.path.join(pkg_path, self.template_paths[t])


class YoloPointFrontendROS(YoloPointFrontend):
    """ROS2 wrapper for YOLOPoint frontend."""

    def __init__(self, node: Node, yolo_cfg: YoloCfg):
        super().__init__(yolo_cfg.config, yolo_cfg, ros=True)
        self.node = node
        self.publish = yolo_cfg.publish
        self.visualize = yolo_cfg.visualize

        # ROS2 publishers
        self.objects_pub = self.node.create_publisher(ObjectInstance2DArray, 'objects', 10)
        self.keypoints_pub = self.node.create_publisher(KeypointArray, 'keypoints', 10)

        # ROS2 subscriber
        self.bridge = CvBridge()
        self.image_sub = self.node.create_subscription(
            Image, yolo_cfg.source, self.callback, 10
        )

        # Load templates
        template_paths = yolo_cfg.template_paths
        if template_paths:
            print("Loading templates...")
            for rostpc, tp in template_paths.items():
                if os.path.exists(tp):
                    template = cv2.imread(tp, 0)
                    template, _, _, _ = self.preprocess(template, interpolation=cv2.INTER_NEAREST)
                    template = cv2.erode(template, np.ones((7, 7), np.uint8), iterations=1)
                    self.templates.update({rostpc: template})
                else:
                    print(f"Template {tp} does not exist")
            print("Templates loaded")

    def callback(self, data: Image):
        try:
            img = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            self.node.get_logger().error(f"CvBridge error: {e}")
            return

        assert img is not None, "No image is being streamed"
        rostpc = data.header.frame_id
        pts, desc, obj_preds = self.process_img(img, rostpc)

        # Publish messages
        self._publish_messages(pts, desc, obj_preds, data.header)
        if self.visualize:
            self.visualize_objects_and_tracks(img, pts, desc, obj_preds)

    def _publish_messages(self, pts, desc, obj_preds, header=None):
        keypoint_msg, array_msg = self.to_ros_msg(pts, desc, obj_preds, header)
        if self.publish:
            self.keypoints_pub.publish(keypoint_msg)
            self.objects_pub.publish(array_msg)

    def to_ros_msg(self, pts, desc, obj_preds, header=None):
        keypoint_msg = KeypointArray()
        if header:
            keypoint_msg.header = header

        keypoint_msg.x = pts[1, :].astype(np.uint16)
        keypoint_msg.y = pts[0, :].astype(np.uint16)
        keypoint_msg.score = pts[2, :].astype(np.float32)
        keypoint_msg.desc_len = np.array(desc.shape[0], dtype=np.uint8)
        keypoint_msg.desc_flat = desc.flatten().astype(float)

        array_msg = ObjectInstance2DArray()
        if header:
            array_msg.header = header

        for det in obj_preds:
            if len(det):
                for *xyxy, conf, cls in reversed(det):
                    c = int(cls)
                    msg = ObjectInstance2D()
                    msg.class_name = self.names[c]
                    msg.class_index = c
                    msg.class_count = len(self.names)
                    msg.class_probabilities = [float(conf)]
                    msg.is_instance = True
                    msg.bounding_box_min_x = int(xyxy[0])
                    msg.bounding_box_min_y = int(xyxy[1])
                    msg.bounding_box_max_x = int(xyxy[2])
                    msg.bounding_box_max_y = int(xyxy[3])
                    array_msg.instances.append(msg)

        return keypoint_msg, array_msg


def main():
    rclpy.init()
    node = Node('yolopoint_node')

    conf = YoloCfg(node)
    fe = YoloPointFrontendROS(node, conf)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down")
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()


if __name__ == "__main__":
    main()