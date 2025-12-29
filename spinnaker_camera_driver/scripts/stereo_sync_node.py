#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Copyright 2024
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------
"""
Stereo Camera Software Synchronization Node

두 대의 카메라를 소프트웨어 기반으로 동기화하는 ROS2 노드입니다.
GPIO 하드웨어 연결 없이 타임스탬프 기반 근사 동기화를 수행합니다.

Usage:
    python3 stereo_sync_node.py
    python3 stereo_sync_node.py --ros-args -p slop:=0.1 -p cam0_topic:=/left/image_raw
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from message_filters import Subscriber, ApproximateTimeSynchronizer
import numpy as np


class StereoSyncNode(Node):
    """두 카메라 이미지를 타임스탬프 기반으로 동기화하는 노드"""

    def __init__(self):
        super().__init__('stereo_sync_node')

        # 파라미터 선언
        self.declare_parameter('cam0_topic', '/left/image_raw')
        self.declare_parameter('cam1_topic', '/right/image_raw')
        self.declare_parameter('slop', 0.1)  # 동기화 허용 오차 (초)
        self.declare_parameter('queue_size', 10)
        self.declare_parameter('publish_synced', True)

        # 파라미터 가져오기
        cam0_topic = self.get_parameter('cam0_topic').value
        cam1_topic = self.get_parameter('cam1_topic').value
        slop = self.get_parameter('slop').value
        queue_size = self.get_parameter('queue_size').value
        self.publish_synced = self.get_parameter('publish_synced').value

        # 통계
        self.sync_count = 0
        self.time_diffs = []
        self.cam0_recv_count = 0
        self.cam1_recv_count = 0

        # 두 카메라 구독 (message_filters 사용)
        self.cam0_sub = Subscriber(self, Image, cam0_topic)
        self.cam1_sub = Subscriber(self, Image, cam1_topic)

        # 수신 카운트용 콜백
        self.cam0_sub.registerCallback(lambda msg: setattr(
            self, 'cam0_recv_count', self.cam0_recv_count + 1))
        self.cam1_sub.registerCallback(lambda msg: setattr(
            self, 'cam1_recv_count', self.cam1_recv_count + 1))

        # 근사 시간 동기화
        self.sync = ApproximateTimeSynchronizer(
            [self.cam0_sub, self.cam1_sub],
            queue_size=queue_size,
            slop=slop
        )
        self.sync.registerCallback(self.sync_callback)

        # 동기화된 이미지 퍼블리셔
        if self.publish_synced:
            self.synced_cam0_pub = self.create_publisher(
                Image, '/synced/cam_0/image_raw', 10)
            self.synced_cam1_pub = self.create_publisher(
                Image, '/synced/cam_1/image_raw', 10)

        # 상태 출력 타이머 (5초마다)
        self.stats_timer = self.create_timer(5.0, self.print_stats)

        self.get_logger().info('=' * 50)
        self.get_logger().info('Stereo Sync Node Started!')
        self.get_logger().info(f'  Cam0 Topic: {cam0_topic}')
        self.get_logger().info(f'  Cam1 Topic: {cam1_topic}')
        self.get_logger().info(f'  Slop: {slop * 1000:.0f}ms')
        self.get_logger().info(f'  Publish synced: {self.publish_synced}')
        self.get_logger().info('=' * 50)

    def sync_callback(self, cam0_msg: Image, cam1_msg: Image):
        """동기화된 이미지 쌍 처리"""
        self.sync_count += 1

        # 타임스탬프 차이 계산
        t0 = cam0_msg.header.stamp.sec + cam0_msg.header.stamp.nanosec * 1e-9
        t1 = cam1_msg.header.stamp.sec + cam1_msg.header.stamp.nanosec * 1e-9
        time_diff_ms = abs(t0 - t1) * 1000
        self.time_diffs.append(time_diff_ms)

        # 동기화된 이미지 재발행
        if self.publish_synced:
            self.synced_cam0_pub.publish(cam0_msg)
            self.synced_cam1_pub.publish(cam1_msg)

        # 로그 출력 (30프레임마다 = 약 1초)
        if self.sync_count % 30 == 0:
            avg_diff = np.mean(self.time_diffs[-30:])
            self.get_logger().info(
                f'[{self.sync_count:5d}] Synced! diff: {time_diff_ms:5.1f}ms '
                f'(avg: {avg_diff:.1f}ms)'
            )

    def print_stats(self):
        """주기적으로 통계 출력"""
        if len(self.time_diffs) == 0:
            self.get_logger().warn('No synchronized frames received!')
            self.get_logger().info(
                f'  Received - CAM0: {self.cam0_recv_count}, '
                f'CAM1: {self.cam1_recv_count}'
            )
            if self.cam0_recv_count == 0 or self.cam1_recv_count == 0:
                self.get_logger().warn('  Check topic names with: ros2 topic list')
            return

        recent = self.time_diffs[-100:]
        self.get_logger().info('=' * 50)
        self.get_logger().info(f'Statistics (last {len(recent)} frames):')
        self.get_logger().info(f'  Total synced: {self.sync_count}')
        self.get_logger().info(f'  Avg diff: {np.mean(recent):.2f}ms')
        self.get_logger().info(
            f'  Min/Max: {np.min(recent):.2f}ms / {np.max(recent):.2f}ms'
        )
        self.get_logger().info('=' * 50)


def main(args=None):
    rclpy.init(args=args)
    node = StereoSyncNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 최종 통계
        if node.time_diffs:
            node.get_logger().info('=' * 50)
            node.get_logger().info('FINAL STATISTICS:')
            node.get_logger().info(f'  Total synced: {node.sync_count}')
            node.get_logger().info(
                f'  Avg diff: {np.mean(node.time_diffs):.2f}ms'
            )
            node.get_logger().info('=' * 50)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
