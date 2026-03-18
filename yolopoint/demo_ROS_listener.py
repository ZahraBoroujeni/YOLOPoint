#!/usr/bin/env python3

import argparse
import numpy as np
import rclpy
from rclpy.node import Node
from keypoint_msg.msg import KeypointArray
from demo import PointTracker
import cv2
from cv_bridge import CvBridge, CvBridgeError
from message_filters import Subscriber, ApproximateTimeSynchronizer


class KeypointListener(Node):
    """Subscriber node that receives keypoints and images and displays tracks."""

    def __init__(self, source_topic, display_scale):
        super().__init__('keypoint_example_node')

        self.bridge = CvBridge()

        # Subscribers using message_filters
        self.image_sub = Subscriber(self, 'sensor_msgs/msg/Image', source_topic)
        self.kp_sub = Subscriber(self, 'keypoint_msg/msg/KeypointArray', '/keypoints')

        self.ts = ApproximateTimeSynchronizer(
            [self.kp_sub, self.image_sub],
            queue_size=10,
            slop=0.5,
        )
        self.ts.registerCallback(self.callback)

        # Tracker parameters
        self.nn_thresh = 0.7
        self.min_length = 2
        self.max_length = 4
        self.tracker = PointTracker(max_length=self.max_length, nn_thresh=self.nn_thresh)

        self.img = None
        self.display_scale = display_scale

    def callback(self, kp_data, img_data):
        coords = np.array([kp_data.y, kp_data.x])
        desc_len = kp_data.desc_len
        desc_flat = np.array(kp_data.desc_flat)
        desc = desc_flat.reshape(desc_len, -1)

        try:
            self.img = self.bridge.imgmsg_to_cv2(img_data, desired_encoding="bgr8")
        except CvBridgeError as e:
            self.get_logger().error(f"CvBridge error: {e}")
            return

        if self.img is None:
            self.get_logger().warn('No image received yet.')
            return

        self._visualize_tracks(coords, desc)

    def _visualize_tracks(self, pts, desc):
        self.tracker.update(pts, desc)

        tracks = self.tracker.get_tracks(self.min_length)
        out = self.img.copy()

        # Normalize track scores to [0,1]
        tracks[:, 1] /= float(self.nn_thresh)
        self.tracker.draw_tracks(out, tracks)

        # Resize if needed
        if self.display_scale != 1.0:
            new_shape = (np.array(out.shape[:2][::-1]) * self.display_scale).astype(int)
            out = cv2.resize(out, new_shape)

        cv2.imshow("Visualization", out)
        cv2.waitKey(1)


def main(args=None):
    parser = argparse.ArgumentParser(description='Keypoint example listener')
    parser.add_argument('source', type=str, help='ROS image topic name, e.g., /camera/image_raw')
    parser.add_argument('--display_scale', type=float, default=1.0,
                        help='Scale factor for visualization (default: 1.0)')
    parsed_args = parser.parse_args()

    rclpy.init(args=args)
    node = KeypointListener(parsed_args.source, parsed_args.display_scale)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()


if __name__ == "__main__":
    main()