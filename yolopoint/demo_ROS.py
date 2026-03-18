#!/usr/bin/env python3
import argparse
import numpy as np
import cv2
import yaml
import os
from glob import glob

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

from object_instance_msgs.msg import ObjectInstance2D, ObjectInstance2DArray
from keypoint_msg.msg import KeypointArray

from yolopoint.demo import YoloPointFrontend


class YoloPointFrontendROS(YoloPointFrontend):
    """Wrapper around pytorch net to help with pre/post image processing."""

    def __init__(self, node: Node, config, args):
        super().__init__(config, args, ros=True)
        self.node = node

        self.publish = args.publish
        self.visualize = args.visualize

        if self.publish:
            self.objects_pub = self.node.create_publisher(ObjectInstance2DArray, 'objects', 10)
            self.keypoints_pub = self.node.create_publisher(KeypointArray, 'keypoints', 10)

        self.bridge = CvBridge()
        if args.source_type == 'ros':
            self.image_sub = self.node.create_subscription(
                Image, args.source, self.callback, 10
            )
        else:
            img_paths = sorted(glob(os.path.join(args.source, '*.png'))) + \
                        sorted(glob(os.path.join(args.source, '*.jpg')))
            assert len(img_paths) > 0, f"Directory {args.source} empty or does not exist"
            self.stream_imgs(img_paths)

        # Load templates
        template_paths = self.config.get('templates')
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

    def callback(self, data):
        try:
            img = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            self.node.get_logger().error(f"CvBridge error: {e}")
            return

        assert img is not None, 'No image is being streamed'
        rostpc = data.header.frame_id
        pts, desc, obj_preds = self.process_img(img, rostpc)

        if self.publish:
            self._publish_messages(pts, desc, obj_preds, data.header)
        if self.visualize:
            self.visualize_objects_and_tracks(img, pts, desc, obj_preds)

    def _publish_messages(self, pts, desc, obj_preds, header=None):
        keypoint_msg, array_msg = self.to_ros_msg(pts, desc, obj_preds, header)
        if self.publish:
            self.keypoints_pub.publish(keypoint_msg)
            self.objects_pub.publish(array_msg)

    def to_ros_msg(self, pts, desc, obj_preds, header):
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

    def stream_imgs(self, img_paths):
        for p in img_paths:
            img = cv2.imread(p)
            pts, desc, obj_preds = self.process_img(img)
            if self.publish:
                self._publish_messages(pts, desc, obj_preds)
            if self.visualize:
                self.visualize_objects_and_tracks(img, pts, desc, obj_preds)


def main():
    parser = argparse.ArgumentParser(description='YOLOPoint Demo ROS2')
    parser.add_argument('config', type=str, default='configs/kitti_inference.yaml')
    parser.add_argument('source_type', type=str, help="Choose 'directory' or 'ros'")
    parser.add_argument('source', type=str, help='Directory or ROS image topic')
    parser.add_argument('--weights_path', type=str, default='logs/YOLOPointS_kitti_nomo/checkpoints/YOLOPointS_kitti_nomo_last_ckpt.pth.tar')
    parser.add_argument('--visualize', action='store_true')
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--display_scale', type=float, default=1.0)
    args = parser.parse_args()

    args.source_type = args.source_type.lower()
    assert args.source_type in {'ros', 'directory'}

    # Load config YAML
    import ament_index_python.packages
    pkg_path = ament_index_python.packages.get_package_share_directory('yolopoint')
    with open(os.path.join(pkg_path, args.config), 'r') as f:
        config = yaml.safe_load(f)

    rclpy.init()
    node = Node('yolopoint_node')

    fe = YoloPointFrontendROS(node, config, args)

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